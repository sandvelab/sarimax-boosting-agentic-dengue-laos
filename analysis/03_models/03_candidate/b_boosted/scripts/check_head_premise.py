"""Check what the head fork predicted before it ran against what it did.

The two children of `02_head` each write a premise into their `model_option_spec.json`
before any model is fitted, and one of them writes an explicit prediction: that a quantile
booster cannot move off zero at any level below the target's zero share. A prediction
registered before the measurement is worth having only if something afterwards compares
the two, and this script is that something. It computes nothing about the world -- every
number it reports is read out of the premise the fork wrote or out of the fitted object the
model wrote -- and it writes the comparison to a file so that the confirmation is an
artifact rather than a reading.

**How "flat at zero" is decided.** The claim was about provinces, so it is measured over
provinces: each level of the stored ladder is evaluated on every row of the analysis
dataset, and a level counts as flat when the largest count it returns anywhere in the file
rounds to zero. A weaker test was tried first and rejected -- bounding each booster by its
baseline plus the largest leaf value of every tree, which needs no data at all. That bound
is over every input the booster could ever be handed, so a single positive leaf reachable
by no actual province makes it non-zero, and it found nothing flat where seven levels
plainly are. The bound answers a different question than the premise asked.

Evaluating the ladder needs the model's own feature construction and its own tree
traversal, so this script imports `boosted.py` from the model directory rather than
rebuilding either. It does not import scikit-learn and does not need to: that is what the
stored form is for.

For the negative-binomial head there is no such prediction to check, and the script records
the fitted dispersion beside the variance-to-mean spread the premise measured, which is the
comparable quantity: one dispersion was fitted where the data's own ratio ranges over
orders of magnitude, and the record should say by how much.

Writes, under results/$COMBO/:
  head_premise_check.json   what was predicted, what happened, and whether they agree
"""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path

import numpy as np
import pandas as pd

NODE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(NODE / "scripts" / "boosted_model"))


def repo_root(start: Path) -> Path:
    for p in [start, *start.parents]:
        if (p / "AGENTS.md").exists():
            return p
    raise SystemExit("no repository root above " + str(start))


ROOT = repo_root(NODE)
COMBO = os.environ.get("COMBO", "main")

sys.path.insert(0, str(ROOT / "analysis" / "scripts" / "lib"))
from combos import resolve, resolve_glob  # noqa: E402

from boosted import add_features, design, raw_predict  # noqa: E402


def ladder_on_the_data(fitted: dict) -> tuple[np.ndarray, pd.DataFrame]:
    """Every level of the stored ladder, evaluated on every row of the analysis dataset.

    Counts, not the log1p scale the boosters were fitted on, so that "flat at zero" is a
    statement about dengue cases and can be read as one.
    """
    dataset, _ = resolve(ROOT / "analysis/02_setup/results", "analysis_dataset.csv")
    frame = pd.read_csv(dataset, dtype={"time_period": str})
    prepared = add_features(frame, fitted["options"])
    X = design(prepared, fitted["options"], fitted["provinces"], fitted["year_base"])
    ladder = np.column_stack([np.maximum(raw_predict(b, X), 0.0)
                              for b in fitted["boosters"]])
    return np.expm1(np.maximum.accumulate(ladder, axis=1)), prepared


def ladder_in_province(ladder: np.ndarray, prepared: pd.DataFrame,
                       provinces: list[str], levels: list[float]) -> dict:
    """The median forecast ladder inside each named province, as counts."""
    out = {}
    for province in provinces:
        mask = (prepared["location"] == province).to_numpy(bool)
        if mask.any():
            out[province] = {
                "median_ladder": [round(float(v))
                                  for v in np.median(ladder[mask], axis=0)],
                "observed_median_count": float(pd.to_numeric(
                    prepared.loc[mask, "disease_cases"], errors="coerce").median()),
                "levels": list(levels),
            }
    return out


def main() -> None:
    out = NODE / "results" / COMBO
    fitted_path = out / "fitted_model.json"
    if not fitted_path.exists():
        raise SystemExit(f"no fitted model for combination {COMBO!r}: {fitted_path} is "
                         f"missing. The model runs before this check.")

    found, from_combo = resolve_glob(
        NODE / "02_head", "*/results/{combo}/model_option_spec.json")
    if len(found) != 1:
        raise SystemExit(f"02_head: expected exactly one child with results for "
                         f"combination {COMBO!r}, found {len(found)}")
    choice = json.loads(found[0].read_text())
    fitted = json.loads(fitted_path.read_text())

    check = {
        "combo": COMBO,
        "head": fitted["head"],
        "premise_from_combo": from_combo,
        "premise_node": choice["node"],
        "source": ["results/<combo>/fitted_model.json",
                   str(found[0].relative_to(ROOT))],
    }

    if fitted["head"] == "quantile_ensemble":
        premise = choice["premise"]
        levels = fitted["quantile_levels"]
        ladder, prepared = ladder_on_the_data(fitted)
        highest = ladder.max(axis=0)
        flat = [level for level, top in zip(levels, highest, strict=True)
                if round(float(top)) == 0]
        stalled = [level for level, rounds in zip(levels, fitted["fit"]["rounds"],
                                                  strict=True) if rounds == 1]
        capped = [level for level, rounds in zip(levels, fitted["fit"]["rounds"],
                                                 strict=True)
                  if rounds == fitted["fit"]["rounds_cap"]]
        predicted = premise["levels_below_the_zero_share"]
        check.update({
            "predicted_before_the_run": choice["predicted_before_the_run"],
            "target_zero_share": premise["target_zero_share"],
            "levels": levels,
            "levels_predicted_flat": predicted,
            "levels_flat_for_every_possible_input": flat,
            "levels_that_took_one_boosting_round": stalled,
            "levels_that_ran_to_the_round_cap": capped,
            "largest_count_each_level_returns_anywhere_in_the_file": dict(
                zip((str(v) for v in levels),
                    (float(v) for v in highest), strict=True)),
            # The province the claim bites hardest for: the one that never reports a zero
            # and is therefore given a lower half of its forecast it can never realise.
            "ladder_in_the_province_that_never_reports_a_zero": ladder_in_province(
                ladder, prepared, premise["provinces_that_never_report_a_zero"], levels),
            "predicted_and_observed_agree": sorted(flat) == sorted(predicted),
            "predicted_but_not_flat": sorted(set(predicted) - set(flat)),
            "flat_but_not_predicted": sorted(set(flat) - set(predicted)),
            "share_of_the_distribution_pinned_at_zero": max(flat) if flat else 0.0,
            "provinces_that_never_report_a_zero":
                premise["provinces_that_never_report_a_zero"],
        })
    else:
        premise = choice["premise"]
        check.update({
            "fitted_dispersion": fitted["dispersion"],
            "variance_to_mean_min": premise["variance_to_mean_min"],
            "variance_to_mean_median": premise["variance_to_mean_median"],
            "variance_to_mean_max": premise["variance_to_mean_max"],
            "what_the_premise_implies": choice["what_the_premise_implies"],
            "predicted_and_observed_agree": None,
        })

    (out / "head_premise_check.json").write_text(
        json.dumps(check, indent=1, sort_keys=True) + "\n")

    if fitted["head"] == "quantile_ensemble":
        print(f"head premise[{COMBO}]: predicted {len(check['levels_predicted_flat'])} "
              f"level(s) flat at zero, found {len(check['levels_flat_for_every_possible_input'])}; "
              f"agree={check['predicted_and_observed_agree']}; "
              f"predicted-but-not-flat {check['predicted_but_not_flat']} -> {out}")
    else:
        print(f"head premise[{COMBO}]: one dispersion {check['fitted_dispersion']:.3f} "
              f"fitted where the data's variance-to-mean runs "
              f"{check['variance_to_mean_min']:.1f}..{check['variance_to_mean_max']:.1f} "
              f"-> {out}")


if __name__ == "__main__":
    main()
