# Clean-room check — 2026-08-26, batch 7

`/validate cleanroom`: build the environment from nothing, run the analysis, and **report
the differences** rather than announcing success.

## What was built

`environment/Dockerfile`, which had never been built — batch 2 wrote it with no Docker
daemon available and marked it "NOT YET VERIFIED", and it has been an open question since.
It builds. The image installs the 174 packages of `environment/lock.txt` into CPython
3.13.0 and reports `chap 2.1.0`, which is what `environment/environment.yml` asks for.

```
docker build -t chap-analysis-env -f environment/Dockerfile .
```

1.62 GB, about seven minutes on this machine, almost all of it downloading wheels.

## What was run, and what could not be

The repository was copied into the container without `.git`, without any virtual
environment, and **without any combination-scoped results**, so nothing could be reused. The
container's own environment replaced `environment/chapenv`.

| Node | Ran | Note |
|---|---|---|
| `01_data` | yes | partition, characterisation, five figures |
| `02_setup` | yes | all four forks and the assembly |
| `03_models/01_baselines` | yes | both baselines, environments built by `uv` inside the container from each model's own lockfile |
| `03_models/02_reference` | **no** | it starts a Docker container, and there is no Docker daemon inside this one |
| `04_score/01_collect`, `02_aggregate` | yes | over the two baselines |
| `04_score/03_compare`, root `conclude.py` | **no** | they need the reference's scores, and it did not run |

**This is the check's real limitation and it is structural, not an oversight.** The project's
reported conclusion is a ratio to an external model that is distributed as a container, so a
clean-room run inside a container cannot produce it without Docker-in-Docker. What can be
verified from nothing is everything up to and including our own models' scores; the
reference's contribution can be verified only on a host with a Docker daemon. Recorded here
so that the next clean-room run does not rediscover it, and so that `/release` does not
claim more than the check supports.

## The differences

**Thirty of the thirty-one files `01_data` produces are byte-identical**, including the
development dataset, the sealed holdout, the backtest scheme and every figure's plotted
values. `02_setup`'s three files are byte-identical.

**Both baselines' per-cell scores are identical** — all 742 rows, every column, so
`metrics_cell.csv`, `metrics_summary.csv`, `crps_by_location.csv`, `crps_by_split.csv` and
`crps_by_horizon.csv` agree exactly. Mean CRPS on both platforms: persistence
24.879338288409706, climatology 24.336908636118597.

Two differences, both real and both small:

**1. One pre-aggregation file differs in the last digit of some floats.**
`fig_cases_seasonality_preaggregation.csv` has `1.8620180051489408` where the host has
`1.8620180051489412` — a one-unit-in-the-last-place difference in a rainfall value, in 2 of
2 592 rows. Nothing else in the file moves and no score anywhere is affected.

The cause is not the pinned package set. It is that pandas' default CSV float parser is
fast rather than correctly rounded, and the macOS-arm64 and linux-arm64 wheels of the same
pandas version disagree by one ULP on some values. **A lockfile pins packages; it does not
pin the compiled code inside them.** The fix, where it matters, is
`pd.read_csv(..., float_precision="round_trip")`.

It does not matter yet, because the only file affected is a re-serialisation of the source
and neither baseline reads a climate covariate. **It will matter in phase C**: the first
candidate that uses rainfall or temperature is reading floats through this parser, and its
forecasts could differ in the last digits between platforms. Phase C's candidates should
read covariates with `float_precision="round_trip"`, and this is the evidence for why.

**2. `crps_by_region_split.csv` differs by 2.8 × 10⁻¹⁴.** Floating-point summation order
inside a `groupby` over a differently ordered frame. Fourteen orders of magnitude below the
smallest difference the analysis can interpret; recorded because "no difference" and "a
difference too small to matter" are different findings.

## What this cost, and what it caught

About twenty minutes, and it caught two things worth more than that.

The first is above. The second was found by accident on the way: an early attempt mounted
the repository **writable** into the container and wrote symlinks into
`environment/chapenv`, breaking the host's analysis environment. Rebuilding it with
`environment/install-chap.sh` then revealed that **the installer resolved `chap-core==2.1.0`
afresh and wrote `lock.txt` from the result, rather than installing from it** — so three
days after the environment was pinned, a rebuild produced `click 8.5.0` where the lockfile
said 8.4.2, along with a dozen other moves, while the file claiming to be what reproduces
sat unchanged in git. `environment/Dockerfile` had always installed from `lock.txt`; the
local installer never had. The two would have drifted apart silently.

`install-chap.sh` now installs from the lockfile when there is one, re-resolves only when
told to with `RESOLVE=1`, and **compares the built environment against the lockfile and
reports the difference** at the end of every build. The environment was rebuilt from the
pinned 174 packages and verified to reproduce the recorded per-cell scores exactly.

That defect was in the repository from batch 2 and no amount of reading would have found it;
it took a rebuild, and the rebuild only happened because something broke. Which is the
argument for running this check on a schedule rather than at submission — stated in
`/validate` before it had an example, and now it has one.
