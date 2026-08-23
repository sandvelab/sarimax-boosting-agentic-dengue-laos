# environment

The **one main environment** for the whole analysis, used generally. A node overrides it
only where it genuinely needs something else, in that node's `env/`, with the reason
recorded in that node's `claim.md`.

Three layers, all produced and verified by `/pin-environment`:

| File | What it is |
|---|---|
| `environment.yml` | Declarative — what was asked for. Readable. |
| `lock.txt` | Resolved — what was actually installed, with versions and hashes. **This is what reproduces.** |
| `Dockerfile` | The whole thing frozen, for when upstream repositories change or disappear. |

Note this is *not* the `.venv` that runs the repository's own machinery (`node.py`,
`check_invariants.py`). That one is a tool; this one is part of the result.

## What cannot be pinned

*(State any dependency that pinning does not survive — a data source behind
authentication, a licence server, specific hardware. Leaving a reproducer to discover it is
the failure this section prevents.)*
