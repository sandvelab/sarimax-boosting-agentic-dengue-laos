# analysis — the claim tree

This is the project. Everything else in the repository is in service of it.

Each node is an **analytical aim** — a question to be explored — with the analysis that
addresses it. `analysis/` is the root node; children are subdirectories. The two
relationship types (`alternatives`, `sub-analyses`) and the shape of a node are specified in
`AGENTS.md` §2 and in `/node`.

**Two properties must always hold.** `analysis/run.sh` reproduces the entire reported
analysis, following the main path at every alternatives fork. And the paths not taken stay
here, complete and runnable — they are executed by the stability node, which calls its
siblings' main scripts.

Never create or rewire nodes by hand:

```bash
.venv/bin/python AI-internal/useful-scripts/node.py tree
.venv/bin/python AI-internal/useful-scripts/node.py new analysis 01_prepare --claim "…"
```

## Currently here

*(Nothing yet — the root node's claim is still a template. Fill in `analysis/claim.md`
first.)*
