# useful-scripts

The repository's own machinery: the code that maintains and checks the analysis, as opposed
to the code that performs it. Every Python script here has a **dual interface** — a
programmatic API and a CLI — so it is useful both as a library and standalone. Invoke as
`.venv/bin/python AI-internal/useful-scripts/<name>.py`.

Note the two interpreters: these run under `.venv` (the repository's tooling), while the
analysis itself runs under the pinned analysis environment declared in `environment/`.

| Script | What it does | Skill |
|---|---|---|
| `node.py` | Create, inspect, promote and rebuild claim-tree nodes, enforcing the alternatives/sub-analyses semantics so they cannot drift by hand | `/node` |
| `check_invariants.py` | The eleven deterministic checks: `tree`, `provenance`, `hashes`, `plots`, `seeds`, `claims`, `combos`, `freeze`, `git`, `crossing`, `pool` | `/validate invariants` |
| `claims.py` | Maintain and audit the claim collection; flag draft sentences with no supporting claim | `/claims` |
| `build_hierarchical_report.py` | Generate the linked static-HTML drill-down report from the tree, down to the per-cell values | `/hierarchical-report` |
| `cleanroom.sh` | Clone the repository, build both environments from nothing, run `analysis/run.sh`, and compare every tracked result byte for byte | `/validate cleanroom` |

`check_invariants.py` exits non-zero on any failure, so it works in a pre-commit hook or CI.
**When it fails, fix the cause — never weaken the check.**

A project may add scripts here as it needs them — a release scanner, a determinism check, a
fork sweep — following this table's format and this file's convention of one row per script.
`cleanroom.sh` was added in batch 19; a release scanner is still owed by ledger row 20.

`cleanroom.sh` is the one shell script here and takes no `--root`: it derives the repository
root from its own location, refuses to run from a dirty tree, and writes its clone and logs to
gitignored paths beside itself.
