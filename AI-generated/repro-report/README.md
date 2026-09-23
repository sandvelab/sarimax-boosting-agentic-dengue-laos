# repro-report

The reproducibility report — the closing step of the project (`/repro-report`): what was
produced, what is tracked and how, the veridical section, the agency record, and what does not
hold. Written from the artefacts, not from a checklist of what should exist.

Every count in the report comes from `inventory.json`, written by
`AI-internal/useful-scripts/repro_inventory.py`, which walks the tree, the provenance records, the
claim collection, the manuscripts' sidecars, the manifests, the plan's decision log and the git
history. The inventory establishes shape; section 5 of the report is written by reading.

## Currently here

- `26-09-23_reproducibilityReport.md` — the report at release (batch 20).
- `inventory.json` — the inventory it cites, regenerable by the script above.
- `provenance.md` — one section per build of the report.
