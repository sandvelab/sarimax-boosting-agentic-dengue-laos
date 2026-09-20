# environment

The **one main environment** for the whole analysis, used generally. A node overrides it
only where it genuinely needs something else, in that node's `env/`, with the reason
recorded in that node's `claim.md`.

Not yet pinned. Fill in `environment.yml` with what the analysis needs, then `/pin-environment`
to produce the lockfile and image, and `/pin-environment verify` to confirm it rebuilds clean.
See `setup-guide.md` at the repository root, §4.

The built environment belongs at `environment/env/` (not tracked; rebuilt from the lockfile),
invoked directly as `environment/env/bin/python` — never by activating it — matching the
convention `AGENTS.md` §8 sets for `.venv`. Node scripts under `analysis/` set `PYTHON`
accordingly; `AI-internal/useful-scripts/node.py` generates them that way.
