# useful-scripts

The repository's own machinery: the code that maintains and checks the analysis, as opposed
to the code that performs it. Every Python script here has a **dual interface** — a
programmatic API and a CLI — so it is useful both as a library and standalone. Invoke as
`.venv/bin/python AI-internal/useful-scripts/<name>.py`, or `bash …/<name>.sh`.

Note the two interpreters: these run under `.venv` (the repository's tooling), while the
analysis itself runs under `environment/chapenv` (the pinned, published environment).
`verify_model_determinism.sh` and `candidate_fork_sweep.py` are the exceptions that call
into the second, because what they run is the analysis.

| Script | What it does | Skill |
|---|---|---|
| `node.py` | Create, inspect, promote and rebuild claim-tree nodes, enforcing the alternatives/sub-analyses semantics so they cannot drift by hand | `/node` |
| `check_invariants.py` | The deterministic checks: tree, provenance, plots, seeds, claims, git, and values crossing steps by hand | `/validate invariants` |
| `claims.py` | Maintain and audit the claim collection; flag draft sentences with no supporting claim | `/claims` |
| `build_hierarchical_report.py` | Generate the linked static-HTML drill-down report from the tree | `/hierarchical-report` |
| `verify_model_determinism.sh` | Rule 6: run each of our models twice under scratch combinations and compare the per-cell scores and the fitted model. Writes to `AI-generated/determinism-checks/` and removes the scratch combinations | — |
| `candidate_fork_sweep.py` | Run every non-main child of candidate 1's forks on the development data, one combination each, and tabulate what they score. Writes its results **into the tree** through the tree's own scripts, and only the cross-combination table to `AI-generated/candidate-forks/`. A phase-C selection aid, not the stability node | — |

`check_invariants.py` exits non-zero on any failure, so it works in a pre-commit hook or CI.
**When it fails, fix the cause — never weaken the check.**
