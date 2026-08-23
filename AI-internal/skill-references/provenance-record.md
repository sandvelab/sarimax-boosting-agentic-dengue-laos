# Provenance record — full specification

Read before writing records, rather than improvising from memory of a previous run.
One file per identifiable result, in the producing node's `provenance/`, named after the
result (`summary.tsv` → `summary.md`).

## Required fields

| Field | Content |
|---|---|
| `result:` | Path relative to the node, e.g. `results/summary.tsv` |
| `script:` | The script that produced it, relative to the node |
| `invocation:` | The **exact** command line, every parameter included |
| `inputs:` | Each input path with a content hash |
| `environment:` | `environment/` (project main), or the node's `env/` |
| `seeds:` | The project seed and the derived component seed |
| `commit:` | The commit the script was at when it ran |
| `instructions-commit:` | The commit `AGENTS.md` and `.claude/` were at |
| `node:` | Path of the node, from the repository root |
| `produced:` | Date |

## Required veridical fields

| Field | Content |
|---|---|
| `alternatives-considered:` | What else could reasonably have been done here, and why it was not |
| `agency:` | `human-set` · `agent-on-human-assessment` · `agent-autonomous` |
| `information:` | `agent-retrieved` · `human-pointed`, where the step rested on gathered information |

A record with only the first block is reproducible but not veridical. `alternatives-considered`
is the field that lets a reader judge whether the analysis was a reasonable one, and it is
the one that cannot be reconstructed later — write it while the reasoning is still in context.

## Worked example

```
result: results/cooccurrence_summary.tsv
script: scripts/summarise_cooccurrence.py
invocation: ../.venv/bin/python scripts/summarise_cooccurrence.py --window 500 --min-count 3
inputs: ../01_prepare/results/regions_filtered.tsv  sha256:9f2c1a…
environment: environment/ (project main)
seeds: project 20260820; component 20260820-summarise
commit: a3f91c2
instructions-commit: 7b21ee9
node: analysis/02_measure/a_jaccard
produced: 2026-08-20
alternatives-considered: a median rather than a mean summary; rejected because the
  distribution is bounded below and the downstream test assumes the mean. A 1000 bp window
  was also reasonable and is run as a perturbation by the stability node.
agency: agent-autonomous
information: human-pointed (window size taken from the protocol in Archive/)
```

## What the invariant checker verifies

That every result has a record, and that each record names an existing script, commit and
environment. It **cannot** verify that a record is true — that the named script is the one
that ran, or that the alternatives listed are the ones considered. Structural checking
narrows where a human must look; it does not remove the need to look.
