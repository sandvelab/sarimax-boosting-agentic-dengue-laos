#!/usr/bin/env bash
# Batch-4 reconnaissance: what already exists in Chap's model library, and what is known
# about whether it runs.
#
# The plan's batch 4 asks what other integrated models could be run and whether any has
# been run on Lao data. Both are answered from two pinned sources rather than from prose:
# the GitHub API listing of github.com/chap-models, and the last published sweep of
# github.com/chap-models/chap-models-checker, which runs `chap eval` against every
# repository in the organisation.
#
# Run from the repository root:  bash AI-internal/reconnaissance/capture_model_library.sh

set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
PY="$ROOT/environment/chapenv/bin/python"
OUT="$ROOT/AI-generated/method-reconnaissance"
WORK="$OUT/library-work"

# The sweep is pinned: its snapshot is a claim about a moment, and an unpinned "current
# status" would make this report un-rereadable a month from now.
CHECKER_REPO="https://github.com/chap-models/chap-models-checker.git"
CHECKER_COMMIT="5f21853e5f3ebd010700b9b1755250d6c69bbbb3"

mkdir -p "$OUT" "$WORK"

echo "== the organisation listing =="
gh api "orgs/chap-models/repos?per_page=100" \
  --jq '.[] | {name, description, language, updated_at, html_url, archived, fork}' \
  > "$WORK/org_repos.jsonl"

echo "== the last published sweep, pinned =="
rm -rf "$WORK/checker"
git clone -q "$CHECKER_REPO" "$WORK/checker"
git -C "$WORK/checker" checkout -q "$CHECKER_COMMIT"
git -C "$WORK/checker" log -1 --format="chap-models-checker %H %cI" > "$OUT/model_library_sources.txt"
echo "org listing fetched $(date -u +%Y-%m-%dT%H:%M:%SZ) from orgs/chap-models/repos" >> "$OUT/model_library_sources.txt"
cp "$WORK/checker/last_report.json" "$OUT/chap_models_checker_report.json"

echo "== joining them into one inventory =="
"$PY" - "$WORK/org_repos.jsonl" "$OUT/chap_models_checker_report.json" "$OUT" <<'PYEOF'
import json
import sys
from pathlib import Path

import pandas as pd

repos_path, report_path, out_dir = Path(sys.argv[1]), Path(sys.argv[2]), Path(sys.argv[3])

repos = pd.DataFrame([json.loads(line) for line in repos_path.read_text().splitlines() if line.strip()])

report = json.loads(report_path.read_text())
checked = pd.DataFrame(
    [
        {
            "name": r["repo"],
            "style": r["style"],
            "sweep_status": r["status"],
            "sweep_failure": r["failure"],
            "sweep_seconds": round(r["duration_s"], 1),
            "sweep_data": r.get("note"),
            "platform_override": r.get("platform_override"),
            "target": r["spec"].get("target"),
            "required_covariates": ",".join(r["spec"].get("required_covariates") or []),
            "additional_continuous_covariates": ",".join(r["spec"].get("additional_continuous_covariates") or []),
            "allows_free_covariates": r["spec"].get("allow_free_additional_continuous_covariates"),
            "period_type": r["spec"].get("supported_period_type"),
            "requires_geo": r["spec"].get("requires_geo"),
            "docker_image": r["spec"].get("docker_image"),
        }
        for r in report["repos"]
    ]
)

inventory = repos.merge(checked, on="name", how="outer").sort_values("name")

# Could this model be pointed at *our* dataset without acquiring new covariates? The Lao
# file carries exactly these, and `chap eval` has no flag for handing a model the polygons,
# so a model that requires geometry is out of reach from the CLI whatever else it needs.
OURS = {"population", "rainfall", "mean_temperature", "mean_relative_humidity"}


def covariates_available(row) -> bool:
    required = {c for c in str(row.get("required_covariates") or "").split(",") if c}
    return required.issubset(OURS)


swept = inventory["sweep_status"].notna()
inventory["covariates_available_in_lao_file"] = inventory.apply(
    lambda row: covariates_available(row) if row["sweep_status"] == row["sweep_status"] else None, axis=1
)
inventory["monthly_capable"] = inventory["period_type"].isin(["month", "any"]).where(swept)
inventory["runnable_on_our_data"] = (
    inventory["covariates_available_in_lao_file"].fillna(False)
    & inventory["monthly_capable"].fillna(False)
    & (inventory["requires_geo"] == False)  # noqa: E712 -- NaN must not count as False here
    & (inventory["sweep_status"] == "pass")
).where(swept)
inventory.to_csv(out_dir / "chap_models_inventory.csv", index=False)

# The two questions the plan asks of the library, answered as counts rather than prose.
summary = {
    "repos_in_org": int(repos.shape[0]),
    "repos_in_last_sweep": int(checked.shape[0]),
    "sweep_pass": int((checked["sweep_status"] == "pass").sum()),
    "sweep_fail": int((checked["sweep_status"] == "fail").sum()),
    "needs_amd64_override": int(checked["platform_override"].notna().sum()),
    # Bracket indexing throughout: `checked.style` is pandas' Styler, not the column.
    "chapkit_style": int((checked["style"] == "chapkit").sum()),
    "mlproject_style": int((checked["style"] == "mlproject").sum()),
    "monthly_or_any_period": int(checked["period_type"].isin(["month", "any"]).sum()),
    "ran_on_curated_lao_subset": int(checked["sweep_data"].fillna("").str.startswith("data=curated").sum()),
    "sweep_reports_any_metric": any(
        key for r in report["repos"] for key in r if "crps" in key.lower() or "metric" in key.lower()
    ),
    "sweep_started_at": report.get("started_at"),
    "in_org_but_not_in_sweep": sorted(set(repos["name"]) - set(checked["name"])),
    "runnable_on_our_data": sorted(inventory.loc[inventory["runnable_on_our_data"] == True, "name"]),  # noqa: E712
    "blocked_by_missing_covariates": sorted(
        inventory.loc[inventory["covariates_available_in_lao_file"] == False, "name"]  # noqa: E712
    ),
}
Path(out_dir / "chap_models_library_summary.json").write_text(json.dumps(summary, indent=2) + "\n")
PYEOF

echo "done -> $OUT/chap_models_inventory.csv"
