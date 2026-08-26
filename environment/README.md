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
| `install-chap.sh` | The build. Creates `chapenv/` **from `lock.txt`**, and re-resolves only with `RESOLVE=1`. |
| `lock.txt` | Resolved — 174 packages with exact versions. **This is what reproduces**, and now it is also what installs. |
| `Dockerfile` | The whole thing frozen, built from `lock.txt`. **Verified: it builds.** |
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

**On 2026-08-26 a third rebuild resolved a different set** — `click 8.5.0` where the
lockfile said 8.4.2, and a dozen other moves — because the script *wrote* `lock.txt` from
what it resolved rather than installing from it. Two runs three days apart had agreed; the
third did not, which is what an unpinned resolution looks like until upstream moves.
`environment/Dockerfile` had always installed from `lock.txt`, so the image and the local
environment would have drifted apart silently.

The script now installs from `lock.txt` when there is one, re-resolves only under
`RESOLVE=1`, and **compares the built environment against the lockfile and prints the
difference** at the end of every build. The environment was rebuilt from the pinned 174
packages and verified to reproduce the recorded per-cell scores exactly. Full account in
`AI-generated/validation/26-08-26_cleanroom.md`.

**The Docker image builds**, verified 2026-08-26: 1.62 GB, CPython 3.13.0, `chap 2.1.0`.
`01_data` and `02_setup` reproduce byte-identically inside it and both baselines reproduce
their per-cell scores exactly. What it cannot run is the reference model node, which starts
a container of its own.

## What cannot be pinned

- **The C libraries inside the pinned packages.** A lockfile pins package versions, not the
  compiled code in them. The macOS-arm64 and linux-arm64 wheels of the same pandas version
  disagree by one unit in the last place on some CSV float parses, which showed up in the
  clean-room run. It affects no score here, because the baselines read no covariate, but
  the first candidate that reads rainfall should use
  `pd.read_csv(..., float_precision="round_trip")`.
- **A clean-room run cannot cover the reference model.** It is distributed as a container
  and this node starts one, so verifying it from nothing needs a Docker daemon outside the
  clean room. Everything up to and including our own models' scores is covered.
- **External models are not in this environment.** Chap runs each model plugin in an
  environment the *model* declares — `uv_env`, `renv_env`, `conda_env` or `docker_env` in
  its `MLproject`, or a container for a chapkit service. Pinning `chap-core` therefore pins
  the platform and the metric, not the models it runs. Each model brings its own pin, and
  models declaring `docker_env` need a Docker daemon; the WHO EWARS reference model needs
  one, on an `amd64` base image.
- **Model code fetched at run time.** `chap eval --model-name <GitHub URL>` clones at run
  time and follows the default branch unless a ref is given, so any model referenced by URL
  is pinned by us, not by the platform.
