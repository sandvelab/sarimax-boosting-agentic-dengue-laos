#!/usr/bin/env python3
"""Describe the development period, 1998-01 to 2009-12, and nothing else.

Its only input is the development file written by the sibling partition node. The
held-out year is not opened here, and no path in this script can reach it.

What it writes, each of it a table another step or a plot reads rather than a number
carried in someone's head:

  dev_overview.json            span, provinces, rows, and the headline completeness
  completeness_by_province_year.csv   observed vs expected target cells per province-year
  target_missing_cells.csv     every province-month whose dengue count is absent
  cases_by_province.csv        totals, zero share, first non-zero month, per province
  cases_by_year.csv            national totals and reporting coverage per year
  cases_national_monthly.csv   the national monthly series, with contributing provinces
  seasonality_by_month.csv     calendar-month profile, nationally and per province
  zero_structure.csv           zeros per province-year -- the zero-heavy early period
  covariate_summary.csv        per-covariate distribution, overall and per province
  covariate_units_check.json   observed magnitudes against the units the schema declares
  population_static_check.csv  whether population varies over time, per province
  lag_correlation.csv          cases against climate at lags 0-6, within province

Seeds: none. Every figure here is a deterministic summary of the file; no procedure
draws randomness, so the project seed 20260822 has no surface.

Usage:  "$PYTHON" scripts/characterise_development.py
"""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd

NODE = Path(__file__).resolve().parent.parent
DEV = NODE.parent / "01_partition" / "results" / "development_1998-01_2009-12.csv"
SCHEMA = NODE.parents[2] / "Archive" / "lao-dataset" / "chap_LAO_admin1_monthly_schema.json"
RESULTS = NODE / "results"

COVARIATES = ["rainfall", "mean_temperature", "mean_relative_humidity"]
MAX_LAG = 6


def load() -> pd.DataFrame:
    df = pd.read_csv(DEV, dtype={"time_period": str})
    df["year"] = df["time_period"].str.slice(0, 4).astype(int)
    df["month"] = df["time_period"].str.slice(5, 7).astype(int)
    return df.sort_values(["location", "time_period"]).reset_index(drop=True)


def overview(df: pd.DataFrame) -> dict:
    observed = int(df["disease_cases"].notna().sum())
    return {
        "file": str(DEV.relative_to(NODE.parents[2])),
        "rows": int(len(df)),
        "provinces": int(df["location"].nunique()),
        "period_first": df["time_period"].min(),
        "period_last": df["time_period"].max(),
        "months": int(df["time_period"].nunique()),
        "grid_is_complete": int(len(df)) == df["location"].nunique() * df["time_period"].nunique(),
        "target_observed_cells": observed,
        "target_missing_cells": int(len(df)) - observed,
        "target_missing_share": round((len(df) - observed) / len(df), 4),
        "target_zero_cells": int((df["disease_cases"] == 0).sum()),
        "target_zero_share_of_observed": round(float((df["disease_cases"] == 0).sum() / observed), 4),
        "total_reported_cases": int(df["disease_cases"].sum()),
        "covariate_missing_cells": {c: int(df[c].isna().sum()) for c in COVARIATES},
    }


def completeness(df: pd.DataFrame) -> pd.DataFrame:
    g = df.groupby(["location", "location_name", "year"], as_index=False).agg(
        cells_expected=("disease_cases", "size"),
        cells_observed=("disease_cases", "count"),
    )
    g["cells_missing"] = g["cells_expected"] - g["cells_observed"]
    g["observed_share"] = (g["cells_observed"] / g["cells_expected"]).round(4)
    return g


def missing_cells(df: pd.DataFrame) -> pd.DataFrame:
    m = df[df["disease_cases"].isna()]
    return m[["location", "location_name", "time_period", "year", "month"]].reset_index(drop=True)


def by_province(df: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for (loc, name), g in df.groupby(["location", "location_name"]):
        obs = g["disease_cases"].dropna()
        nonzero = g[g["disease_cases"].fillna(0) > 0]["time_period"]
        rows.append({
            "location": loc,
            "location_name": name,
            "population": int(g["population"].iloc[0]),
            "cells_observed": int(len(obs)),
            "cells_missing": int(g["disease_cases"].isna().sum()),
            "total_cases": int(obs.sum()),
            "mean_cases": round(float(obs.mean()), 3) if len(obs) else np.nan,
            "median_cases": float(obs.median()) if len(obs) else np.nan,
            "max_cases": int(obs.max()) if len(obs) else 0,
            "zero_months": int((obs == 0).sum()),
            "zero_share": round(float((obs == 0).mean()), 4) if len(obs) else np.nan,
            "first_nonzero_period": nonzero.min() if len(nonzero) else "-",
            "last_nonzero_period": nonzero.max() if len(nonzero) else "-",
            "cases_per_100k_per_year": round(
                float(obs.sum() / (g["population"].iloc[0] / 1e5) / (len(obs) / 12)), 2
            ) if len(obs) else np.nan,
        })
    return pd.DataFrame(rows).sort_values("total_cases", ascending=False).reset_index(drop=True)


def by_year(df: pd.DataFrame) -> pd.DataFrame:
    g = df.groupby("year", as_index=False).agg(
        cells_expected=("disease_cases", "size"),
        cells_observed=("disease_cases", "count"),
        total_cases=("disease_cases", "sum"),
        provinces_reporting=("location", "nunique"),
    )
    reporting = (df.dropna(subset=["disease_cases"])
                   .groupby("year")["location"].nunique().rename("provinces_with_any_observation"))
    g = g.merge(reporting, on="year", how="left").fillna({"provinces_with_any_observation": 0})
    g["total_cases"] = g["total_cases"].astype(int)
    g["provinces_with_any_observation"] = g["provinces_with_any_observation"].astype(int)
    g["observed_share"] = (g["cells_observed"] / g["cells_expected"]).round(4)
    return g


def national_monthly(df: pd.DataFrame) -> pd.DataFrame:
    g = df.groupby("time_period", as_index=False).agg(
        total_cases=("disease_cases", "sum"),
        provinces_observed=("disease_cases", "count"),
        provinces_expected=("location", "nunique"),
    )
    g["total_cases"] = g["total_cases"].astype(int)
    g["year"] = g["time_period"].str.slice(0, 4).astype(int)
    g["month"] = g["time_period"].str.slice(5, 7).astype(int)
    # A national total over a varying number of reporting provinces is not comparable
    # across months; the mean per reporting province is, and both are stored.
    g["mean_cases_per_reporting_province"] = (
        g["total_cases"] / g["provinces_observed"].replace(0, np.nan)).round(3)
    return g


def seasonality(df: pd.DataFrame) -> pd.DataFrame:
    national = df.groupby("month", as_index=False).agg(
        mean_cases=("disease_cases", "mean"),
        median_cases=("disease_cases", "median"),
        total_cases=("disease_cases", "sum"),
        cells_observed=("disease_cases", "count"),
        **{f"mean_{c}": (c, "mean") for c in COVARIATES},
    )
    national.insert(0, "scope", "national")
    national.insert(1, "location", "ALL")
    per = df.groupby(["location", "month"], as_index=False).agg(
        mean_cases=("disease_cases", "mean"),
        median_cases=("disease_cases", "median"),
        total_cases=("disease_cases", "sum"),
        cells_observed=("disease_cases", "count"),
        **{f"mean_{c}": (c, "mean") for c in COVARIATES},
    )
    per.insert(0, "scope", "province")
    out = pd.concat([national, per], ignore_index=True)
    num = out.select_dtypes("number").columns
    out[num] = out[num].round(3)
    return out


def zero_structure(df: pd.DataFrame) -> pd.DataFrame:
    g = df.groupby(["location", "location_name", "year"], as_index=False).agg(
        cells_observed=("disease_cases", "count"),
        zero_months=("disease_cases", lambda s: int((s.dropna() == 0).sum())),
        total_cases=("disease_cases", "sum"),
    )
    g["total_cases"] = g["total_cases"].astype(int)
    g["zero_share"] = (g["zero_months"] / g["cells_observed"].replace(0, np.nan)).round(4)
    return g


def covariate_summary(df: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for scope, key in (("overall", None), ("province", "location")):
        groups = [("ALL", df)] if key is None else list(df.groupby("location"))
        for name, g in groups:
            for c in COVARIATES:
                s = g[c].dropna()
                rows.append({
                    "scope": scope, "location": name, "covariate": c,
                    "n": int(len(s)), "min": round(float(s.min()), 5),
                    "p05": round(float(s.quantile(0.05)), 5),
                    "median": round(float(s.median()), 5),
                    "mean": round(float(s.mean()), 5),
                    "p95": round(float(s.quantile(0.95)), 5),
                    "max": round(float(s.max()), 5),
                    "sd": round(float(s.std()), 5),
                })
    return pd.DataFrame(rows)


def units_check(df: pd.DataFrame) -> dict:
    """Test the schema's declared units against the magnitudes actually in the file.

    The schema calls `rainfall` a total in millimetres accumulated over the month. Two
    readings of the same column are possible -- a monthly total, or a mean daily rate --
    and they differ by roughly the length of a month, so the implied annual rainfall
    separates them by a factor of about thirty. Both are computed and stored; which one
    describes a monsoon climate is then a question about the number, not about the
    schema's prose."""
    schema = json.loads(SCHEMA.read_text())
    declared = {f["name"]: f["unit"] for f in schema["fields"]}
    descriptions = {f["name"]: f.get("description", "") for f in schema["fields"]}
    out = {"declared_units": declared, "observed": {}}
    for c in COVARIATES:
        s = df[c].dropna()
        out["observed"][c] = {
            "declared_unit": declared.get(c),
            "min": round(float(s.min()), 5),
            "p05": round(float(s.quantile(0.05)), 5),
            "median": round(float(s.median()), 5),
            "p95": round(float(s.quantile(0.95)), 5),
            "max": round(float(s.max()), 5),
        }

    # Implied annual rainfall per province under each reading, averaged over provinces.
    days = df["time_period"].map(
        lambda tp: pd.Period(tp, freq="M").days_in_month).astype(float)
    per_year_as_total = (df.assign(v=df["rainfall"])
                           .groupby(["location", "year"])["v"].sum()
                           .groupby("location").mean())
    per_year_as_daily_rate = (df.assign(v=df["rainfall"] * days)
                                .groupby(["location", "year"])["v"].sum()
                                .groupby("location").mean())
    out["rainfall_reading"] = {
        "schema_description": descriptions.get("rainfall"),
        "implied_annual_mm_if_column_is_a_monthly_total": {
            "min_province": round(float(per_year_as_total.min()), 1),
            "median_province": round(float(per_year_as_total.median()), 1),
            "max_province": round(float(per_year_as_total.max()), 1),
        },
        "implied_annual_mm_if_column_is_a_mean_daily_rate": {
            "min_province": round(float(per_year_as_daily_rate.min()), 1),
            "median_province": round(float(per_year_as_daily_rate.median()), 1),
            "max_province": round(float(per_year_as_daily_rate.max()), 1),
        },
        "ratio_between_readings": round(float(days.mean()), 3),
        "note": (
            "Read as a monthly total, the column puts a province's whole year at a few "
            "tens of millimetres, which no inhabited part of mainland Southeast Asia "
            "receives. Read as a mean daily rate in mm/day it puts the year in the "
            "thousands, and the monthly profile in seasonality_by_month.csv peaks in "
            "the southwest-monsoon months. The second reading is the one the file "
            "supports; the schema's 'total precipitation aggregated over the time "
            "bucket, mm' does not describe this column. Nothing downstream depends on "
            "which is true -- the models see a monotone transform of the same numbers -- "
            "but anything importing an external rainfall threshold does, and would be "
            "wrong by a factor of about thirty."
        ),
    }
    return out


def population_static(df: pd.DataFrame) -> pd.DataFrame:
    g = df.groupby(["location", "location_name"], as_index=False).agg(
        distinct_values=("population", "nunique"),
        value=("population", "first"),
        min_value=("population", "min"),
        max_value=("population", "max"),
    )
    g["is_static_over_time"] = g["distinct_values"] == 1
    return g


def lag_correlation(df: pd.DataFrame) -> pd.DataFrame:
    """Spearman correlation of the dengue count with each climate covariate at lags 0-6,
    computed within province and then pooled, so the between-province differences in
    level do not masquerade as a climate signal."""
    rows = []
    for c in COVARIATES:
        for lag in range(MAX_LAG + 1):
            per_province = []
            for loc, g in df.groupby("location"):
                g = g.sort_values("time_period")
                x = g[c].shift(lag)
                y = g["disease_cases"]
                ok = x.notna() & y.notna()
                if ok.sum() >= 24:
                    per_province.append((loc, float(x[ok].corr(y[ok], method="spearman"))))
            vals = [v for _, v in per_province if not np.isnan(v)]
            rows.append({
                "covariate": c, "lag_months": lag,
                "provinces_used": len(vals),
                "mean_spearman": round(float(np.mean(vals)), 4) if vals else np.nan,
                "median_spearman": round(float(np.median(vals)), 4) if vals else np.nan,
                "min_spearman": round(float(np.min(vals)), 4) if vals else np.nan,
                "max_spearman": round(float(np.max(vals)), 4) if vals else np.nan,
                "provinces_positive": int(sum(v > 0 for v in vals)),
            })
    return pd.DataFrame(rows)


def main() -> int:
    RESULTS.mkdir(exist_ok=True)
    df = load()

    (RESULTS / "dev_overview.json").write_text(json.dumps(overview(df), indent=2) + "\n")
    (RESULTS / "covariate_units_check.json").write_text(json.dumps(units_check(df), indent=2) + "\n")

    tables = {
        "completeness_by_province_year.csv": completeness(df),
        "target_missing_cells.csv": missing_cells(df),
        "cases_by_province.csv": by_province(df),
        "cases_by_year.csv": by_year(df),
        "cases_national_monthly.csv": national_monthly(df),
        "seasonality_by_month.csv": seasonality(df),
        "zero_structure.csv": zero_structure(df),
        "covariate_summary.csv": covariate_summary(df),
        "population_static_check.csv": population_static(df),
        "lag_correlation.csv": lag_correlation(df),
    }
    for name, table in tables.items():
        table.to_csv(RESULTS / name, index=False)

    print(f"development: {len(df)} rows, {df['location'].nunique()} provinces, "
          f"{df['time_period'].nunique()} months")
    print(f"target missing in {int(df['disease_cases'].isna().sum())} cells; "
          f"zeros in {int((df['disease_cases'] == 0).sum())}")
    print(f"wrote {len(tables) + 2} files to {RESULTS.relative_to(NODE.parents[2])}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
