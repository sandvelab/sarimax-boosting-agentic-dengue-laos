"""The ensemble candidate: its members, its weights, and the pool it draws from.

Imported by `train.py` and `predict.py`, which are thin, for the reason the other two
candidates' modules give: logic written twice is logic that will eventually be written two
different ways.

## The model

Candidate 3 fits nothing of its own. It is a **linear opinion pool** over the models this
project already has — the two candidate families and the two required baselines — and its
only content is how the members are combined:

    F(y) = sum_m w_m F_m(y)

the members' predictive *distributions* averaged, not their point forecasts. Averaging
distributions and averaging points are different models, and the difference is the whole
reason this node can be worth having: a pool of point forecasts throws away every member's
uncertainty and then has to invent a new one, while a pool of distributions keeps all of
it and adds the disagreement between the members as extra spread.

## Where the members come from

**They are not reimplemented here.** Each member is run through **its own Chap entry
points, exactly as chap-core would run them** — the command string is read out of the
member's own `MLproject` and its placeholders filled in, so this model talks to its members
through the same contract the platform does. There is therefore one copy of each member's
code in the repository, at the node that owns it, and a change to a member is a change to
this model with no file here to keep in step.

The members, their model directories and their configurations are named in a file this
model is pointed at, assembled by the node above (`prepare_members.py`). That file is
hashed into the configuration, so a run records not only which members were pooled but the
exact bytes of every member's contract directory and configuration.

The one thing this costs: the model's environment must be able to run all of its members,
so it is the union of theirs. That is stated in `pyproject.toml` rather than discovered.

## Where the weights come from

`01_weighting` is the fork, and the two children are genuinely different kinds of answer.

* **`equal`** — every member weighs `1/M`. Nothing is estimated, so nothing can be
  overfitted, and the pool carries as much of the two baselines as of the two candidates.
* **`min_crps`** — the weights that minimise the pool's own CRPS on a validation period
  **held back from inside the training frame**. For sample-based forecasts,

        CRPS(F, y) = E|X - y| - 0.5 E|X - X'|

  so for the pool it is `sum_m w_m A_m - 0.5 w' B w` with `A_m = E_{F_m}|X - y|` and
  `B_mk = E|X_m - X'_k|`, both averaged over the validation cells. That is a small
  quadratic programme, convex on the simplex because the matrix of expected absolute
  differences between distributions is conditionally negative definite. It is solved, not
  searched: projected gradient from the equal-weight point, and the answer is then checked
  against every single-member solution and against equal weights, so the fit can never
  return something worse than the alternatives it was supposed to improve on.

The validation period is the last `validation_blocks` forecast blocks of whatever frame
`train` is handed, and every member is **refitted on the frame with those blocks removed**
before being scored on them. Scoring the members' full-frame fits on rows they were fitted
on would hand the weights to whichever member fits its own training data hardest, which is
a property of a model this project has no interest in.

## The forecast draw

The pool is sampled rather than evaluated in closed form, because two of the four members
have no closed form. Each member is asked for its own 1 000 draws through its own
`predict`, and the pool's 1 000 draws are allocated across the members in proportion to
their weights by the largest-remainder rule and then drawn from each member's set without
replacement. Allocating exactly rather than drawing a member per sample removes one source
of Monte Carlo noise from the pool and leaves the draw an exact sample of the mixture.

## What this model cannot do

It cannot be better than its best member at everything, and it will usually be worse than
the best member wherever that member is right and the others are not — a pool is a hedge.
What it can do is be wrong less often in the places where the best member fails, which on
this dataset is a per-province question rather than an average one. That is what the
node's results are read for.
"""

from __future__ import annotations

import hashlib
import json
import shlex
import subprocess
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import yaml

# Draws per cell. Matched to the reference model's 1 000 posterior draws, to both
# baselines and to both other candidates, so the sample-based CRPS of every model in the
# project is computed at the same resolution.
N_SAMPLES = 1000

DEFAULTS = {
    "weighting": "equal",
    "validation_blocks": 4,
    "weight_samples": 200,
    "members_file": "",
    "members_sha256": "",
    "seed": 0,
}

# Declared in MLproject and implemented here. A value declared but not implemented is a
# sibling node's job to bring code for, and saying so is what stops a configuration from
# silently selecting a path nobody wrote.
IMPLEMENTED = {"weighting": ("equal", "min_crps")}


# --------------------------------------------------------------------------- options


def repo_root(start: Path) -> Path:
    for p in [start.resolve(), *start.resolve().parents]:
        if (p / "AGENTS.md").exists():
            return p
    raise SystemExit("no repository root above " + str(start))


ROOT = repo_root(Path(__file__))


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read_options(path: str | Path) -> dict:
    """The model configuration, as chap-core hands it to the entry points."""
    document = yaml.safe_load(Path(path).read_text()) or {}
    values = document.get("user_option_values") or {}
    unknown = sorted(set(values) - set(DEFAULTS))
    if unknown:
        raise SystemExit(f"unknown model option(s) {unknown}; this model declares "
                         f"{sorted(DEFAULTS)} in its MLproject")
    options = {**DEFAULTS, **values}
    for key, allowed in IMPLEMENTED.items():
        if options[key] not in allowed:
            raise SystemExit(
                f"option {key}={options[key]!r} is declared but not implemented; "
                f"this model implements {list(allowed)}. The sibling node that would "
                f"take this path has to bring its own code.")
    options["validation_blocks"] = int(options["validation_blocks"])
    options["weight_samples"] = int(options["weight_samples"])
    return options


def read_members(options: dict) -> list[dict]:
    """The members of the pool, from the file the node above assembled.

    The file's hash is in the configuration, so a members file edited after the
    configuration was written is a failure here rather than a run whose record names
    something other than what it pooled.
    """
    if not options["members_file"]:
        raise SystemExit("no members_file in the configuration; this model pools other "
                         "models and cannot be run without being told which")
    path = ROOT / options["members_file"]
    if not path.exists():
        raise SystemExit(f"members file {path} does not exist")
    digest = sha256(path)
    if options["members_sha256"] and digest != options["members_sha256"]:
        raise SystemExit(
            f"the members file has changed since the configuration was assembled:\n"
            f"  configuration says sha256:{options['members_sha256']}\n"
            f"  {path} is sha256:{digest}\n"
            f"Refusing to pool a set of models the record would misname.")
    members = json.loads(path.read_text())["members"]
    if not members:
        raise SystemExit(f"{path} lists no members")
    return members


# ----------------------------------------------------------------- running a member


def entry_command(member: dict, entry: str, values: dict[str, str]) -> list[str]:
    """One member's own entry-point command, with chap-core's placeholders filled in.

    Read from the member's `MLproject` rather than written here. That is what makes this
    model a consumer of the Chap contract rather than a second implementation of four
    other models: whatever chap-core would run to train or to forecast with a member is
    what runs, and a member that changes its command line changes this call with it.
    """
    spec = member["entry_points"][entry]
    command = spec["command"]
    for name in spec["parameters"]:
        if name not in values:
            raise SystemExit(f"{member['name']}: its {entry} entry point declares "
                             f"parameter {name!r}, which this model cannot supply")
        command = command.replace("{" + name + "}", shlex.quote(str(values[name])))
    left = [part for part in command.split() if part.startswith("{")]
    if left:
        raise SystemExit(f"{member['name']}: unfilled placeholder(s) {left} in its "
                         f"{entry} command")
    parts = shlex.split(command)
    # The member's command names `python`; the interpreter that must run it is this
    # model's, because this model's environment is the union of its members' and the
    # member's own is not built here.
    if parts[0] != "python":
        raise SystemExit(f"{member['name']}: its {entry} command starts with "
                         f"{parts[0]!r}, and this model only knows how to run `python`")
    return [sys.executable, *parts[1:]]


def run_member(member: dict, entry: str, values: dict[str, str]) -> None:
    command = entry_command(member, entry, values)
    directory = ROOT / member["model_dir"]
    result = subprocess.run(command, cwd=directory, capture_output=True, text=True)
    if result.returncode != 0:
        raise SystemExit(
            f"{member['name']}: {entry} failed ({result.returncode}) in {directory}\n"
            f"$ {' '.join(command)}\n{result.stdout}\n{result.stderr}")


def member_config_value(member: dict) -> str:
    """The member's configuration file, as an absolute path, or '' if it takes none."""
    return str(ROOT / member["model_config"]) if member.get("model_config") else ""


def train_members(members: list[dict], frame: pd.DataFrame, work: Path) -> dict:
    """Fit every member on `frame` through its own `train` entry point.

    Returns each member's fitted object, parsed. Every model in this project writes its
    fitted object as JSON -- Rule 5 -- which is what makes it embeddable here: the pool's
    own fitted object can carry its members whole, so `predict` needs nothing but the file
    chap-core hands it.
    """
    work.mkdir(parents=True, exist_ok=True)
    data = work / "train_data.csv"
    frame.to_csv(data, index=False)

    fitted = {}
    for member in members:
        out = work / f"{member['name']}.model.json"
        run_member(member, "train", {
            "train_data": data, "model": out,
            "model_config": member_config_value(member)})
        fitted[member["name"]] = json.loads(out.read_text())
    return fitted


def predict_members(members: list[dict], fitted: dict, historic: pd.DataFrame,
                    future: pd.DataFrame, work: Path) -> dict[str, pd.DataFrame]:
    """Ask every member for its own draws on the same forecast rows.

    Each member gets exactly the two frames chap-core would give it, written to files, and
    returns exactly the CSV chap-core would read. The frames are written once and shared,
    so a member cannot be handed a different history than another.
    """
    work.mkdir(parents=True, exist_ok=True)
    historic_path, future_path = work / "historic.csv", work / "future.csv"
    historic.to_csv(historic_path, index=False)
    future.to_csv(future_path, index=False)

    out = {}
    for member in members:
        model_path = work / f"{member['name']}.model.json"
        model_path.write_text(json.dumps(fitted[member["name"]], indent=1, sort_keys=True))
        forecast = work / f"{member['name']}.forecast.csv"
        run_member(member, "predict", {
            "model": model_path, "historic_data": historic_path,
            "future_data": future_path, "out_file": forecast,
            "model_config": member_config_value(member)})
        frame = pd.read_csv(forecast, dtype={"time_period": str})
        out[member["name"]] = frame.set_index(["location", "time_period"]).sort_index()
    return out


# ------------------------------------------------------------------------- the pool


def sample_columns(frame: pd.DataFrame) -> list[str]:
    columns = [c for c in frame.columns if c.startswith("sample_")]
    return sorted(columns, key=lambda c: int(c.split("_")[1]))


def stacked(forecasts: dict[str, pd.DataFrame], names: list[str]) -> tuple[np.ndarray, list]:
    """Every member's draws on the common cells, as an (M, cells, draws) array.

    The cells are the ones **every** member returned. A member that dropped a cell would
    otherwise be silently averaged into a pool of a different shape, and a pool whose
    membership varies by cell is not the model this node claims to be.
    """
    index = None
    for name in names:
        keys = forecasts[name].index
        index = keys if index is None else index.intersection(keys)
    index = index.sort_values()
    block = np.stack([
        forecasts[name].loc[index, sample_columns(forecasts[name])].to_numpy(float)
        for name in names])
    return block, list(index)


def project_simplex(v: np.ndarray) -> np.ndarray:
    """Euclidean projection onto the probability simplex (Duchi et al., 2008)."""
    u = np.sort(v)[::-1]
    cumulative = np.cumsum(u) - 1.0
    rho = np.nonzero(u - cumulative / np.arange(1, len(v) + 1) > 0)[0][-1]
    theta = cumulative[rho] / (rho + 1.0)
    return np.maximum(v - theta, 0.0)


def crps_terms(block: np.ndarray, observed: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    """`A` and `B` of the pooled-CRPS quadratic, averaged over cells.

    `A_m` is member m's mean absolute distance from the outcome; `B_mk` is the mean
    absolute distance between a draw of member m and an independent draw of member k. Both
    are the sample forms of the terms in `CRPS = E|X - y| - 0.5 E|X - X'|`, which is what
    makes the pool's CRPS a quadratic in the weights rather than something to search over.
    """
    members, cells, draws = block.shape
    A = np.abs(block - observed[None, :, None]).mean(axis=2).mean(axis=1)
    B = np.zeros((members, members))
    for m in range(members):
        for k in range(m, members):
            # (cells, draws, draws) one pair at a time: the whole tensor at once would be
            # M^2 times larger for no gain, and this is already the expensive line.
            value = np.abs(block[m][:, :, None] - block[k][:, None, :]).mean(axis=(1, 2))
            B[m, k] = B[k, m] = value.mean()
    return A, B


def pooled_crps(weights: np.ndarray, A: np.ndarray, B: np.ndarray) -> float:
    return float(weights @ A - 0.5 * weights @ B @ weights)


def min_crps_weights(A: np.ndarray, B: np.ndarray, iterations: int = 4000) -> dict:
    """The weights on the simplex at which the pool's CRPS is smallest.

    Projected gradient from equal weights, then compared against every single-member
    solution and against equal weights. The comparison is not a safety net bolted on: a
    fitted weight vector that scores worse on its own objective than the constant it was
    initialised at would mean the solve failed, and the run should say so rather than
    return it.
    """
    members = len(A)
    equal = np.full(members, 1.0 / members)
    step = 1.0 / (np.abs(B).sum(axis=1).max() + 1e-12)

    weights = equal.copy()
    for _ in range(iterations):
        weights = project_simplex(weights - step * (A - B @ weights))

    named = {"solved": weights, "equal": equal}
    for m in range(members):
        vertex = np.zeros(members)
        vertex[m] = 1.0
        named[f"member_{m}"] = vertex
    best = min(named, key=lambda key: pooled_crps(named[key], A, B))

    return {
        "weights": named[best].tolist(),
        "chosen": best,
        "objective": {key: pooled_crps(value, A, B) for key, value in named.items()},
        "solver": {"method": "projected gradient on the simplex", "iterations": iterations,
                   "step": step, "started_from": "equal weights"},
    }


def allocate(weights: np.ndarray, total: int) -> np.ndarray:
    """How many of the pool's draws each member contributes, by largest remainder.

    Exact allocation rather than drawing a member per sample: the pool is then an exact
    sample of the mixture with one fewer source of Monte Carlo noise, and a member whose
    weight is small still contributes its share in every cell instead of by luck.
    """
    exact = weights * total
    counts = np.floor(exact).astype(int)
    short = total - counts.sum()
    if short:
        order = np.argsort(-(exact - counts))
        counts[order[:short]] += 1
    return counts


def pool(block: np.ndarray, weights: np.ndarray, rng: np.random.Generator,
         total: int = N_SAMPLES) -> np.ndarray:
    """Draw the pool's samples for every cell, in a fixed order over cells."""
    counts = allocate(weights, total)
    members, cells, draws = block.shape
    out = np.empty((cells, total))
    for cell in range(cells):
        pieces = [rng.choice(block[m][cell], size=counts[m], replace=counts[m] > draws)
                  for m in range(members) if counts[m]]
        sample = np.concatenate(pieces)
        out[cell] = rng.permutation(sample)
    return out
