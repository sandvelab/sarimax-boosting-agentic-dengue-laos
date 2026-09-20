#!/usr/bin/env python3
"""Can stage 1's out-of-sample errors be predicted better than chance from forecast-time
information -- and by how much, for which features, with which model family?

Reads `results/test_cells.csv` (never the terminal). Target: z = error / stage-1 se, the
standardised error, so that provinces of every scale pool on one footing and a predicted
z-hat converts back to a correction z-hat * se on each province's own scale -- the
scale-preserving pooling `e_pooledRandomForest`'s failure asked for.

**Design**: leave-one-split-out cross-validation over the 8 backtest splits (train on 7
splits' cells, predict the 8th), for every (feature set x model family). Reported per
configuration: skill = 1 - MSE(z - z-hat) / MSE(z) (zero means no better than predicting no
correction; negative means worse), the mean CRPS of stage 1's mean plus the correction with
sigma unchanged, and 90% coverage. **"Chance" is made concrete** rather than assumed: the
same model on the same features with the target z permuted across cells, repeated
N_PERMUTATIONS times, gives the distribution of skill a model achieves when there is nothing
to find; a configuration is better than chance when its skill exceeds the permutation
distribution's 95th percentile.

**What this is and is not**: an exploratory, cross-validated estimate on the development
backtest's own test cells -- it trains on later splits to predict earlier ones, so it is not
a candidate's score and is never reported as one. Its role is to say which features and
families are worth building into a leakage-safe stage-2 candidate (which trains only inside
each split's training window), and to set the expectation for how much such a candidate can
gain. That dual use is logged in the plan's §4b.

**Seeds** (Rule 6): the random forest, the gradient booster and the permutations all draw
randomness; each is pinned via `component_seed("05_residualStructure")`.
"""
from __future__ import annotations

import csv
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.ensemble import GradientBoostingRegressor, RandomForestRegressor
from sklearn.linear_model import Ridge
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler

NODE = Path(__file__).resolve().parents[1]
ANALYSIS = NODE.parents[0]
sys.path.insert(0, str(ANALYSIS / "scripts"))
from lib.crps import crps_gaussian  # noqa: E402
from lib.project_seed import component_seed  # noqa: E402

RESULTS = NODE / "results"
CELLS_CSV = RESULTS / "test_cells.csv"
SEED = component_seed("05_residualStructure")
Z90 = 1.6448536269514722
N_PERMUTATIONS = 30

ZCLIP = 3.0  # training target is z winsorised here; |z|>3 cells are the reporting-regime breaks
MONTH_DUMMIES = [f"m{k}" for k in range(1, 13)]

FEATURE_SETS = {
    "calendar_only": ["sin_m", "cos_m"],
    "calendar_h": ["sin_m", "cos_m", "h"],
    "month_dummies_h": MONTH_DUMMIES + ["h"],
    "lag12_calendar (earlier candidates' input)": ["r_lag12", "sin_m", "cos_m"],
    "recent_residuals": ["r_last", "r_last3", "h"],
    "recent_plus_national": ["r_last", "r_last3", "nat_last3", "h"],
    "climate_anomalies": ["rain_anom", "temp_anom", "hum_anom", "rain_anom3", "temp_anom3", "hum_anom3", "h"],
    "level": ["level_std", "log_train_mean", "h"],
    "incidence_anomalies": ["inc_anom3", "nat_inc_anom3", "h"],
    "susceptibility_reporting": ["cum12_anom", "cum36_anom", "zero_frac24", "h"],
    "recent_national_level": ["r_last", "r_last3", "nat_last3", "level_std", "log_train_mean", "h", "sin_m", "cos_m"],
    "incidence_recent_level_month": ["inc_anom3", "nat_inc_anom3", "r_last", "r_last3", "level_std",
                                     "log_train_mean", "cum12_anom", "zero_frac24", "h"] + MONTH_DUMMIES,
    "all_no_climate": ["r_last", "r_last3", "r_lag12", "nat_last3", "level_std", "log_train_mean", "h",
                       "inc_anom3", "nat_inc_anom3", "cum12_anom", "cum36_anom", "zero_frac24"] + MONTH_DUMMIES,
    "all": ["r_last", "r_last3", "r_lag12", "nat_last3", "rain_anom", "temp_anom", "hum_anom",
            "rain_anom3", "temp_anom3", "hum_anom3", "level_std", "log_train_mean", "h",
            "inc_anom3", "nat_inc_anom3", "cum12_anom", "cum36_anom", "zero_frac24"] + MONTH_DUMMIES,
}


def families(seed: int) -> dict:
    return {
        "ridge": lambda: make_pipeline(StandardScaler(), Ridge(alpha=1.0)),
        "ridge_strong": lambda: make_pipeline(StandardScaler(), Ridge(alpha=30.0)),
        "random_forest": lambda: RandomForestRegressor(
            n_estimators=100, max_depth=4, min_samples_leaf=10, max_features="sqrt",
            random_state=seed, n_jobs=1),
        "gradient_boosting": lambda: GradientBoostingRegressor(
            n_estimators=100, max_depth=2, learning_rate=0.05, subsample=0.8,
            min_samples_leaf=10, random_state=seed),
    }


def loso_predict(df: pd.DataFrame, feats: list[str], make_model, y: np.ndarray) -> np.ndarray:
    """Leave-one-split-out predictions of y from feats; NaN features are filled with the
    training fold's column means (a feature missing at forecast time carries no information)."""
    pred = np.full(len(df), np.nan)
    X = df[feats].to_numpy(float)
    splits = df["split"].to_numpy()
    for s in np.unique(splits):
        tr, te = splits != s, splits == s
        Xtr, Xte = X[tr].copy(), X[te].copy()
        means = np.nanmean(Xtr, axis=0)
        for j in range(X.shape[1]):
            Xtr[np.isnan(Xtr[:, j]), j] = means[j]
            Xte[np.isnan(Xte[:, j]), j] = means[j]
        m = make_model()
        m.fit(Xtr, y[tr])
        pred[te] = m.predict(Xte)
    return pred


def skill(target: np.ndarray, pred: np.ndarray) -> float:
    return float(1 - np.mean((target - pred) ** 2) / np.mean(target ** 2))


def score(df: pd.DataFrame, zhat: np.ndarray, zw: np.ndarray) -> dict:
    """Skill on the winsorised target (what was fit), skill on the raw z, and -- the objective
    that matters -- CRPS in case units once zhat*se is added to stage 1's mean."""
    z = df["z"].to_numpy()
    mu = df["mu1"].to_numpy() + zhat * df["se1"].to_numpy()
    se = df["se1"].to_numpy()
    crps = float(np.mean([crps_gaussian(a, m, max(s, 1e-6)) for a, m, s in zip(df["actual"], mu, se)]))
    cov = float(np.mean(np.abs((df["actual"].to_numpy() - mu) / se) <= Z90))
    per_h = {}
    for h in sorted(df["h"].unique()):
        sel = (df["h"] == h).to_numpy()
        per_h[f"h{int(h)}"] = skill(zw[sel], zhat[sel])
    return {"skill_winsorised_z": skill(zw, zhat), "skill_raw_z": skill(z, zhat), "skill_by_horizon": per_h,
            "mean_crps_corrected": crps, "coverage_90": cov,
            "mean_abs_correction_in_z": float(np.mean(np.abs(zhat))),
            "share_final_mean_negative": float(np.mean(mu < 0))}


def main() -> None:
    df = pd.read_csv(CELLS_CSV)
    cm = df["month"].str[5:7].astype(int)
    for k in range(1, 13):
        df[f"m{k}"] = (cm == k).astype(float)
    z = df["z"].to_numpy(float)
    zw = np.clip(z, -ZCLIP, ZCLIP)
    fams = families(SEED)
    rng = np.random.default_rng(SEED)
    stage1_crps = float(df["crps1"].mean())
    stage1_cov = float(np.mean(np.abs(z) <= Z90))

    rows, detail = [], {}
    for fs_name, feats in FEATURE_SETS.items():
        for fam_name, make in fams.items():
            zhat = loso_predict(df, feats, make, zw)
            real = score(df, zhat, zw)
            perm_skills = []
            for _ in range(N_PERMUTATIONS):
                zp = rng.permutation(zw)
                zhat_p = loso_predict(df, feats, make, zp)
                perm_skills.append(skill(zp, zhat_p))
            perm_skills = np.array(perm_skills)
            p95 = float(np.quantile(perm_skills, 0.95))
            rows.append({
                "feature_set": fs_name, "family": fam_name, "n_features": len(feats),
                "skill_winsorised_z": real["skill_winsorised_z"], "skill_raw_z": real["skill_raw_z"],
                "skill_h1": real["skill_by_horizon"].get("h1"),
                "skill_h2": real["skill_by_horizon"].get("h2"), "skill_h3": real["skill_by_horizon"].get("h3"),
                "mean_crps_corrected": real["mean_crps_corrected"],
                "pct_change_crps_vs_stage1": 100 * (real["mean_crps_corrected"] - stage1_crps) / stage1_crps,
                "coverage_90": real["coverage_90"],
                "share_final_mean_negative": real["share_final_mean_negative"],
                "mean_abs_correction_in_z": real["mean_abs_correction_in_z"],
                "permutation_skill_mean": float(perm_skills.mean()),
                "permutation_skill_p95": p95,
                "better_than_chance": bool(real["skill_winsorised_z"] > p95),
            })
            detail[f"{fs_name} | {fam_name}"] = {**real, "permutation_skills": perm_skills.tolist()}

    rows.sort(key=lambda r: r["mean_crps_corrected"])
    with (RESULTS / "predictability.csv").open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)

    best = rows[0]
    summary = {
        "design": "leave-one-split-out CV over 8 backtest splits on 02_stage1's test cells; target = z = "
                  f"error/se winsorised at +/-{ZCLIP} for fitting; correction = zhat*se added to stage 1's "
                  f"mean, sigma unchanged; chance = same model on permuted target, {N_PERMUTATIONS} "
                  "permutations, threshold = 95th percentile of permutation skill",
        "seed": SEED,
        "stage1_alone": {"mean_crps": stage1_crps, "coverage_90": stage1_cov, "skill": 0.0},
        "n_configurations": len(rows),
        "n_better_than_chance": int(sum(r["better_than_chance"] for r in rows)),
        "n_beating_stage1_crps": int(sum(r["mean_crps_corrected"] < stage1_crps for r in rows)),
        "best_by_crps": best,
        "best_skill": max(rows, key=lambda r: r["skill_winsorised_z"]),
        "earlier_candidates_input": [r for r in rows if r["feature_set"].startswith("lag12_calendar")],
        "per_configuration": detail,
    }
    (RESULTS / "predictability.json").write_text(json.dumps(summary, indent=2) + "\n")
    print(json.dumps({k: v for k, v in summary.items() if k != "per_configuration"}, indent=2))


if __name__ == "__main__":
    main()
