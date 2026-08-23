# useful-scripts

Every script has a **dual interface**: a programmatic API and a CLI, so it is useful both as
a library and standalone. Invoke as `.venv/bin/python AI-internal/useful-scripts/<name>.py`.

| Script | What it does | Skill |
|---|---|---|
| `node.py` | Create, inspect, promote and rebuild claim-tree nodes, enforcing the alternatives/sub-analyses semantics so they cannot drift by hand | `/node` |
| `check_invariants.py` | The deterministic checks: tree, provenance, plots, seeds, claims, git, and values crossing steps by hand | `/validate invariants` |
| `claims.py` | Maintain and audit the claim collection; flag draft sentences with no supporting claim | `/claims` |
| `build_hierarchical_report.py` | Generate the linked static-HTML drill-down report from the tree | `/hierarchical-report` |

`check_invariants.py` exits non-zero on any failure, so it works in a pre-commit hook or CI.
**When it fails, fix the cause — never weaken the check.**
