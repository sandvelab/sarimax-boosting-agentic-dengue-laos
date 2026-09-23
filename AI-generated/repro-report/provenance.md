# provenance — `repro-report/`

One section per build of the reproducibility report. Append; never overwrite an existing section.

---

## Build 1 — 2026-09-23 (batch 20, release)

script: `AI-internal/useful-scripts/repro_inventory.py`
        sha256:98487d2459ee151c72fb9bbb3a1c58c4cfa04991e72bd38500238936fbff66a3
invocation: `.venv/bin/python AI-internal/useful-scripts/repro_inventory.py`
        (the repository's own machinery, so `.venv`, not the pinned analysis environment; it
        also runs `check_invariants.py` and records its verdict)
inputs: the tree — every `analysis/**/claim.md`, `scripts/`, `results/`, `run.sh` and
        `provenance/*.md`; `Human-AI-collaboration/claims/claims.md`; every
        `Human-AI-collaboration/manuscript/*_claims.md` sidecar and its draft;
        `analysis/06_stability/results/manifest.csv`, `manifest_holdout.csv`,
        `manifest_freeze.json`, `holdout_freeze.json`, `run_status_holdout.csv`; the plan's
        §4b and §6; `environment/`; `AI-generated/validation/*/summary.json`; the git history.
output: `inventory.json` (sha256:ade480f1f48003ff16ac42f913d8536d9216ca00c8e7fb7c4b6fa509b639fc2d), produced at commit `b8941c4`
        on a clean working tree, with all eleven invariants holding;
        `26-09-23_reproducibilityReport.md`, written from it by the agent.
commit: b8941c4 (the inventory ran here; the report and this record are committed in the
        commit that follows, so the report's own commit is one later than the head it cites)
instructions-commit: cadd306 (the last change to `AGENTS.md` or `.claude/`)
node: not a node; a view over the whole repository.
produced: 2026-09-23

**What the report's sections rest on.** Sections 1–4 give counts and every count is a field of
`inventory.json`; the qualitative statements in section 1 are the claims' (C1–C32), and those in
section 3 the stability node's (C2–C20). Section 5, what does not hold, was written by reading:
the records the inventory flags as missing a field, the outsider tests' findings, the release
scan's output, the batch reports, and the scripts themselves (the unpinned `uv`). Nothing in it
comes from a computation the inventory did not do.

alternatives-considered: writing the report from a checklist of what should exist — rejected;
  `/repro-report` asks that it degrade gracefully against a project that followed none of the
  rules, which a checklist cannot. Counting by hand from the tree — rejected under Rule 1, which
  is why the inventory script exists.
agency: agent-autonomous.
information: none retrieved; every input is a file in this repository.
