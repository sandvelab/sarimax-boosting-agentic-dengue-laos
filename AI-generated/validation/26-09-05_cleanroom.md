# Clean-room — 2026-09-05, batch 19

`/validate cleanroom`, the fifth run and the second to finish. **`analysis/run.sh` exited 0
from a clean checkout in 53 514 s (891 min, 14.87 h)**, at commit `6d6ad7c`, covering both
Lao datasets, the two sibling countries, all sixty-nine combinations, both distributions, the
external check and the last script in the tree.

Batch 31 was the first run to reach the end. This is the first to do so **with
`analysis/06_external` in the tree**, which is what the reproducibility report named as the
one thing its verification did not cover.

## The headline

**Every model this project wrote returned an identical score, and the reference did not.**

| | archived | clean-room |
|---|---|---|
| development, our pool | **18.816872064690028** | **18.816872064690028** |
| development, the reference | 22.098446 | 22.060330 |
| development skill | +0.148498 | +0.147027 |
| held-out year, our pool | **76.73108261979166** | **76.73108261979166** |
| held-out year, the reference | 84.026202 | 82.369720 |
| held-out skill | +0.086820 | +0.068455 |

Across every leaderboard in the tree, **552 model-combination scores** were compared:
**207 from models we wrote came back identical and none moved**; of 345 reference scores, 340
moved and 5 did not. That is the project's central claim, stated as sharply as it can be
made: *`analysis/run.sh` reproduces this analysis from nothing, and the qualification belongs
in the same breath — our models are bit-identical, the model we are measured against is an
unseeded container, and every figure that divides by it is a draw.*

2 511 of 4 790 tracked files came back byte-identical.

## The four defences, all holding from cold

Each was written after an earlier clean-room run exited 1, and each was tested here against a
fresh draw that disagreed with the record — which is the only condition under which passing
means anything.

| defence | batch | verdict on this run |
|---|---|---|
| the frozen phase-E set | 24 | **"the frozen set is intact"**, `manifest_holdout.csv` still `fc9d1a16…`, 33 rows; the cost-column drift reported and non-fatal |
| the recorded tier-1 order and tier-2 selection | 26 | **"the rule would now choose 6 different pair(s); the recorded ones stand"** |
| the frozen development figure against a moved pairing | 30 | held; the run passed the step that stopped batch 27 |
| **the external plan's recorded estimate** | **20** | **`rows_agree: true`, 4 estimates drifted, manifest not rewritten** |

The last of those is its **first cold test**, and it is the one worth dwelling on. Batch 20's
external plan divides a measured wall-clock duration, and `05_stability/run.sh` rewrites that
duration one step before the external node runs. From cold the unit moved from **2.2568 to
2.1505 seconds per cell** — so a plan that recomputed itself would have come back with four
different estimates and the claim that it was committed before the rows ran would have been a
claim about a file that had since been rewritten. It was verified instead, and the drift was
reported. **That defect was found by asking what the next clean-room run would do, and this is
the run that would have found it.**

## What this run found that the previous one could not

### The external check's band clause does not survive a re-run, in two of three countries

Batch 20 reported that the development-to-final-year drop replicates on both sibling
countries and that **all three drops are larger than the two reference bands they are measured
against, taken together**. The drop replicates on this run too. The clause about the bands
does not.

| country | archived drop | clean-room drop | clears the two bands? |
|---|---|---|---|
| Laos | −0.0617 | −0.0786 | True → **False** |
| Vietnam | −0.1714 | −0.1419 | True → True |
| Thailand | −0.0659 | −0.0345 | True → **False** |

The Lao fragility was predicted: batch 19's outsider check found that the Lao drop cleared its
band sum by only 0.0207 while the Lao development band had been drawn as wide as 0.0483, and
C42's scope was amended on 2026-09-05 to say so before this run landed.

**Thailand was not predicted, and it failed differently.** Thailand has the tightest band in
the project — 0.032 CRPS, a two-hundredth of Vietnam's — so its clause was the safest of the
three. What moved was not the band but the **drop itself**, from −0.0659 to −0.0345, because
the Thai final-year skill nearly tripled from +0.0197 to +0.0498 while the development skill
barely moved. The reference model happened to do worse on Thailand's 2010 this time.

**What survives and what does not.** The direction survives everywhere: all three countries
drop, on both draws. The ordering survives: Vietnam largest, Laos and Thailand smaller. The
sign of the Vietnamese final-year result survives — the model loses to the reference there on
both runs. **The clause that quantifies the drop against the reference's own noise does not
survive**, and it should never have been stated without its draw-dependence, on the standard
the human set on 2026-09-03 for exactly this kind of sentence.

C42 is corrected accordingly, and the case write-up with it.

### Cost, and the correction it makes to batch 20's own finding

| half | planned | actual | ratio |
|---|---|---|---|
| external check, as run in batch 20 | 11 292.9 s | 6 517.0 s | 0.58 |
| external check, from cold | 11 292.9 s | **5 034.8 s** | **0.45** |

Batch 20 concluded that the cost model was out by a factor of about two because seconds per
evaluated cell measured on 192 Lao cells does not transfer to 1 824 Thai ones. From cold it is
out by a factor of 2.2, in the same direction — so that reading holds, and the estimate is if
anything more conservative than batch 20 said.

The whole run took 14.87 h against batch 31's 11.6 h. **The difference is not the external
check**, which is 1.4 h of it. About three of the remaining hours are contention: the agent
ran the external check, two outsider agent sessions, a release scan over 8 875 git blobs and a
hierarchical-report build on the same host while an emulated amd64 container was the run's
bottleneck. Measured rather than inferred: the run completed 7 rows in its first nine hours
and 17 in the hour after the agent went quiet. **A clean-room run wants the machine, and this
one did not get it for the first two thirds of its life** — recorded here because the elapsed
figure would otherwise be read as a property of the analysis.

## What is still not verified

**The `choose_weighting.py` premise defect is in this run's output, unfixed.** The outsider
check found it after the run was launched, so this run reproduces the tree that carries it —
which is the point: batch 32 builds its defence against **this run's own files**, as batch 26
built against batch 25's, batch 30 against batch 27's and batch 28 against batch 31's.

**The two hardcoded absolute paths in the clean-room harness itself.**
`run_cleanroom.sh` and `cleanroom_compare.py` each name this machine's repository path as a
constant, so the harness only runs here. Found by the release scan; fixed after this run
finished, because bash reads a running script by byte offset and editing it mid-run is not
safe.

**The write-into-the-tree half of the outsider check**, which was killed by an account spend
limit and is unrelated to this run except that both bear on whether an outsider could use this
repository.

## How it was run

`git clone` of the repository at `6d6ad7c` into `AI-internal/useful-scripts/repo`,
`environment/chapenv` built from `environment/lock.txt`, then `bash analysis/run.sh` from
cold, on the host, with Docker available. The clone carried no `.holdout_opened`, so the seal
released and phase E ran rather than being described.

The harness is `AI-internal/useful-scripts/run_cleanroom.sh`, unchanged. The run was launched
detached under `caffeinate -ims`, so the 891 minutes are a measurement rather than a wall
clock across a sleeping host.

**The scratch clone is now gitignored** rather than deleted by hand. Batches 18, 25, 27 and 31
each removed it before committing; it is 20 GB inside the repository it is checking, and a
forgotten removal would stage twenty gigabytes. Its findings are in
`26-09-05_cleanroom-artefacts/` and the clone is discarded.

---

**Agency:** agent-autonomous. That `/validate cleanroom` runs before release is the plan's
(phase E); the run, the comparisons and the readings are the agent's.
