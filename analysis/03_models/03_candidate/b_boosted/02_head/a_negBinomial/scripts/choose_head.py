"""Stage 2 of candidate 2's configuration: a negative binomial around the fitted mean.

One booster, fitted for the conditional mean under a Poisson deviance loss, and a single
negative-binomial dispersion estimated by maximum likelihood on that fit. The predictive
distribution is then a negative binomial per cell whose mean is the trees' output and
whose variance is `mu + mu^2 / phi`.

**What this head assumes, and why the assumption is checkable.** The width of every
forecast is a fixed function of its level: two cells with the same predicted mean get the
same distribution, however differently the model was placed to predict them. That is a
strong assumption, and it is the one candidate 1's own diagnosis put under suspicion —
batch 9 found its width wrong locally rather than on average, in two provinces at opposite
ends. This head cannot repair that by construction, and the sibling is where a per-cell
width gets its chance.

What can be checked before the run is whether one dispersion is even the right order of
thing to ask for. The premise below measures the variance-to-mean ratio of the target
within each province: if it were near one everywhere, a Poisson head would do and the
negative binomial would be answering a question nobody asked; if it varies by orders of
magnitude across provinces, a single shared dispersion is being asked to cover all of it,
and the number saying by how much belongs in the record before the CRPS does.

**Why the mean booster uses a Poisson deviance loss rather than squared error on a
transform.** The target is a count over a population that differs a hundredfold between
provinces. Squared error on the raw count would fit Vientiane Capital and ignore the rest;
squared error on log1p would fit a median rather than a mean, which is not what a
negative-binomial head is then built around. The Poisson deviance is the loss whose
minimiser is the conditional mean of a count, and it carries the log link that keeps the
prediction positive.

Writes, under results/$COMBO/:
  model_option_spec.json   the choice, its option values, and the premise it rests on
"""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path

import numpy as np
import pandas as pd

NODE = Path(__file__).resolve().parents[1]


def repo_root(start: Path) -> Path:
    for p in [start, *start.parents]:
        if (p / "AGENTS.md").exists():
            return p
    raise SystemExit("no repository root above " + str(start))


ROOT = repo_root(NODE)
COMBO = os.environ.get("COMBO", "main")

sys.path.insert(0, str(ROOT / "analysis" / "scripts" / "lib"))
from combos import resolve  # noqa: E402


def main() -> None:
    out = NODE / "results" / COMBO
    out.mkdir(parents=True, exist_ok=True)

    dataset, dataset_combo = resolve(
        ROOT / "analysis/02_setup/results", "analysis_dataset.csv")
    frame = pd.read_csv(dataset, dtype={"time_period": str})
    counts = pd.to_numeric(frame["disease_cases"], errors="coerce")

    # Variance-to-mean per province, over the whole development file. One is what a
    # Poisson would imply; anything far above it is what the negative binomial's extra
    # parameter exists to carry.
    ratios = {}
    for location, block in frame.groupby("location"):
        y = pd.to_numeric(block["disease_cases"], errors="coerce").dropna()
        if len(y) > 1 and y.mean() > 0:
            ratios[str(location)] = float(y.var(ddof=1) / y.mean())
    spread = sorted(ratios.values())

    spec = {
        "combo": COMBO,
        "input_from_combo": dataset_combo,
        "stage": "head",
        "order": 2,
        "node": str(NODE.relative_to(ROOT)),
        "choice": "a_negBinomial",
        "description": ("one booster for the conditional mean under a Poisson deviance "
                        "loss, and a negative binomial around it at a single dispersion "
                        "estimated by maximum likelihood on the training fit"),
        "user_option_values": {"head": "negative_binomial"},
        "additional_continuous_covariates": [],
        "premise": {
            "rows": int(len(frame)),
            "target_observed": int(counts.notna().sum()),
            "target_zero_share": float((counts.fillna(-1) == 0).sum()
                                       / max(int(counts.notna().sum()), 1)),
            "variance_to_mean_by_province": ratios,
            "variance_to_mean_min": spread[0] if spread else None,
            "variance_to_mean_median": (float(np.median(spread)) if spread else None),
            "variance_to_mean_max": spread[-1] if spread else None,
            "poisson_would_imply": 1.0,
        },
        # Registered before the run.
        "what_the_premise_implies": (
            "a single shared dispersion is being asked to cover the whole spread of "
            "variance-to-mean ratios recorded above; the wider that spread, the more of "
            "the calibration error this head cannot reach"),
    }
    (out / "model_option_spec.json").write_text(
        json.dumps(spec, indent=1, sort_keys=True) + "\n")

    print(f"head/a_negBinomial[{COMBO}]: variance-to-mean by province "
          f"{spread[0]:.1f}..{spread[-1]:.1f} (Poisson would be 1.0) -> {out}")


if __name__ == "__main__":
    main()
