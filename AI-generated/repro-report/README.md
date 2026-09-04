# repro-report

The closing report of the project (Rule 10, via `/repro-report`): what was produced, what is
tracked and how, what the veridical work established, who decided what, and what does not
hold.

It is written from the artefacts rather than from a checklist of what should exist, which is
what lets it degrade gracefully — run against a project that followed none of these rules it
would still say honestly what little could be established.

## Currently here

- `26-09-05_reproducibilityReport.md` — batch 19. Its §5, *what does not hold*, is the
  section to read first: the unseeded reference model every ratio divides by, the reported
  figure that reproduced while what it counts changed, the clean-room verification's lag
  behind the tree, a Rule 5 failure in the project's own plan-drift machinery, and the
  decision-recording defect this repository found four separate times.
- `repro_inventory.json` — what the repository contains, counted by walking it. The report
  quotes these figures and computes none of its own.
- `provenance.md` — the record for both.

Regenerate the inventory with
`.venv/bin/python AI-internal/useful-scripts/repro_inventory.py`. The figures are a function
of the commit it is run at, and `counted_at_commit` says which. The narrative is written by
hand from it and is dated; earlier ones are never overwritten.
