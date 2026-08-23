# environment

The **one main environment** for the whole analysis, used generally. A node overrides it
only where it genuinely needs something else, in that node's `env/`, with the reason
recorded in that node's `claim.md`.

Everything the analysis reports is produced by `chap eval`, so pinning this environment
pins the metric, the backtest arithmetic and the model runner in a single step. That is why
there is only one thing in it.

| File | What it is |
|---|---|
| `environment.yml` | Declarative — what was asked for: CPython 3.13.0 and `chap-core==2.1.0`. |
| `install-chap.sh` | The build. Creates `chapenv/` and writes `lock.txt`. |
| `lock.txt` | Resolved — 174 packages with exact versions. **This is what reproduces.** |
| `Dockerfile` | The whole thing frozen, built from `lock.txt`. Specification only — see below. |
| `chapenv/` | The built environment. Not tracked; rebuild it with `install-chap.sh`. |

Invoke it directly, as `environment/chapenv/bin/chap` and `environment/chapenv/bin/python` —
never by activating it — matching the convention `AGENTS.md` §8 sets for `.venv`.

Note this is *not* the `.venv` at the repository root, which runs the repository's own
machinery (`node.py`, `check_invariants.py`). That one is a tool; this one is part of the
result.

## What has been verified

`install-chap.sh` was run twice on 2026-08-23, the second time after deleting `chapenv/`
entirely. Both runs resolved the identical 174 packages, which is why the Python patch
version is pinned: `uv venv --python 3.13` picks whichever 3.13 the building machine
happens to hold, and that is not a specification.

## What cannot be pinned

- **The Docker image has never been built.** No Docker daemon was running on the machine
  that wrote the `Dockerfile`, so the third layer is a specification and not a verified
  artifact. `/pin-environment verify` is what would settle it.
- **External models are not in this environment.** Chap runs each model plugin in an
  environment the *model* declares — `uv_env`, `renv_env`, `conda_env` or `docker_env` in
  its `MLproject`, or a container for a chapkit service. Pinning `chap-core` therefore pins
  the platform and the metric, not the models it runs. Each model brings its own pin, and
  models declaring `docker_env` need a Docker daemon; the WHO EWARS reference model needs
  one, on an `amd64` base image.
- **Model code fetched at run time.** `chap eval --model-name <GitHub URL>` clones at run
  time and follows the default branch unless a ref is given, so any model referenced by URL
  is pinned by us, not by the platform.
