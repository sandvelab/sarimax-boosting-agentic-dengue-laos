"""Stage 4 of the common setup: every model is refitted at every split.

chap-core's `n-retrain` says how many evenly spaced points across the backtest the
estimator is retrained at. The sibling takes the platform's default of one: a single fit
on the training period, with the expanding historic window handed to `predict` at every
split thereafter. This child sets it to the number of splits, so each split's forecast is
made by a model that has been refitted on everything up to it.

**Why it is a fork and not an obvious improvement.** Refitting at every split is closer to
how a forecasting system is actually operated, and it is what the reference model does
inside its own `predict` whatever this flag says. But it multiplies the fitting cost of
every model in the comparison by the number of splits, and it changes the comparison's
shape as well as its cost: under one fit, later splits are forecast by a model that has
not seen the intervening year, so the backtest measures how fast a fitted model goes
stale. Both are defensible readings of "how well does this model forecast", and which one
the headline number describes is exactly the sort of choice this project refuses to leave
implicit.

**The value is read, not typed.** `n_retrain` may not exceed `n_splits` -- chap-core
rejects the parameter set if it does -- so the number here has to be the split count of
the scheme actually in force. It is read from the same stored scheme file and the same
key that `02_setup/scripts/assemble_setup.py` reads `n_splits` from, so the two cannot
disagree. When phase E switches that lookup to the holdout scheme, this stage moves with
it or `/validate invariants` has two files to compare rather than one number to trust.

This stage changes no data.

Writes, under results/$COMBO/:
  analysis_dataset.csv   the dataset as it leaves the setup chain
  setup_spec.json        the chosen retrain policy, as an eval flag
"""

from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path

NODE = Path(__file__).resolve().parents[1]
SETUP = NODE.parents[1]

SCHEME = "analysis/01_data/02_characterise/results/backtest_scheme_chosen.json"
# The same key `assemble_setup.py` reads the rest of the backtest flags from.
SCHEME_KEY = "development_scheme"


def repo_root(start: Path) -> Path:
    for p in [start, *start.parents]:
        if (p / "AGENTS.md").exists():
            return p
    raise SystemExit("no repository root above " + str(start))


ROOT = repo_root(NODE)
COMBO = os.environ.get("COMBO", "main")


def upstream(fork: str, combo: str) -> Path:
    found = sorted((SETUP / fork).glob(f"*/results/{combo}/analysis_dataset.csv"))
    if len(found) != 1:
        raise SystemExit(
            f"{fork}: expected exactly one child with results for combination "
            f"{combo!r}, found {[str(p.relative_to(SETUP)) for p in found]}")
    return found[0]


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read_table(path: Path) -> tuple[str, list[str]]:
    """The file as its header line and its data lines, unparsed. See `a_once`."""
    text = path.read_text()
    header, _, body = text.partition("\n")
    return header, [line for line in body.split("\n") if line]


def write_table(path: Path, header: str, rows: list[str]) -> None:
    path.write_text(header + "\n" + "".join(line + "\n" for line in rows))


def main() -> None:
    out = NODE / "results" / COMBO
    out.mkdir(parents=True, exist_ok=True)

    scheme = json.loads((ROOT / SCHEME).read_text())
    n_splits = int(scheme[SCHEME_KEY]["n_splits"])

    source = upstream("03_provinces", COMBO)
    header, rows = read_table(source)
    write_table(out / "analysis_dataset.csv", header, rows)

    spec = {
        "combo": COMBO,
        "stage": "retrain",
        "order": 4,
        "node": str(NODE.relative_to(ROOT)),
        "choice": "b_everySplit",
        "description": "refit at every split: n_retrain set to the scheme's n_splits",
        "dataset_transform": "identity",
        "n_retrain_source": f"{SCHEME} -> {SCHEME_KEY}.n_splits",
        "input": str(source.relative_to(ROOT)),
        "input_sha256": sha256(source),
        "output_sha256": sha256(out / "analysis_dataset.csv"),
        "rows_in": len(rows),
        "rows_out": len(rows),
        "eval_flags": {"n_retrain": n_splits},
    }
    (out / "setup_spec.json").write_text(json.dumps(spec, indent=1, sort_keys=True) + "\n")

    print(f"retrain/b_everySplit: n_retrain={n_splits} (= n_splits), "
          f"{len(rows)} rows pass through")


if __name__ == "__main__":
    main()
