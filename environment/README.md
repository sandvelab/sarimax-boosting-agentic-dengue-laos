# environment

The **one main environment** for the whole analysis, used generally. A node overrides it
only where it genuinely needs something else, in that node's `env/`, with the reason
recorded in that node's `claim.md`.

Native Python — no Chap, no Docker (plan §4, batch 1). Pinned batch 2.

| File | What it is |
|---|---|
| `environment.yml` | Declarative — CPython 3.13, `pandas`, `numpy`, `scipy`, `statsmodels` (stage 1), `properscoring` (verification reference for the CRPS implementation, not used to score), `scikit-learn` (tree-based stage-2 candidate, batch 5). |
| `install-env.sh` | The build. Creates `env/` **from `lock.txt`**, and re-resolves only with `RESOLVE=1`, reporting any difference between what it built and that file. |
| `lock.txt` | Resolved — 18 packages with exact versions (`uv pip freeze`). **This is what reproduces.** |
| `env/` | The built environment. Not tracked; rebuild with `install-env.sh`. |

Invoke directly, as `environment/env/bin/python` — never by activating it — matching the
convention `AGENTS.md` §8 sets for `.venv`. Note this is *not* the `.venv` at the repository
root, which runs the repository's own machinery (`node.py`, `check_invariants.py`).

## What has been verified

`install-env.sh` was run twice on 2026-09-20: once with `RESOLVE=1` (resolved and wrote
`lock.txt`), once without (installed from `lock.txt`, into a freshly recreated `env/`, and
confirmed the built environment matches the lockfile exactly).

Re-verified 2026-09-20 (batch 5) after adding `scikit-learn` for the tree-based stage-2
candidate: same two-pass check, `RESOLVE=1` then a clean rebuild from the resulting
`lock.txt`, confirmed to match exactly (18 packages).

No Dockerfile yet — this is a lightweight native-Python pipeline with no compiled
platform-specific model runner (unlike the prior project's Chap/R-INLA reference), so an
image is not judged worth the upkeep unless a later stage-2 family needs one.
