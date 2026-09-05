# Release — 2026-09-05, batch 19

`/release`: the safety scan, the assembly, and what is cleared to be pushed. **Nothing has
been pushed.** No remote exists; `/release` never pushes without asking, and the agent asks
before the push whatever else has been settled (plan §10).

Every figure here is read from `release_scan.json` and `release_manifest.json` beside this
file. Nothing was counted by eye.

---

## The safety scan

### Credentials — clean

| | |
|---|---|
| tracked files scanned | **4 840** |
| git objects scanned, history included | **8 875 blobs** |
| credential pattern matches, working tree | **0** |
| credential pattern matches, history | **0** |
| credential files by name (`.env`, `.pem`, `id_rsa`, service-account JSON, …) | **0** |

Ten patterns: provider-prefixed API keys for five providers, PEM private-key headers,
`Authorization: Bearer` lines, connection strings carrying an inline password, and the
generic `key/token/secret/password =` assignment. Every blob the history holds was streamed
and scanned by hash, so a credential removed in a later commit would still have been found.

### Data permission — cleared, and it had to be asked

All five archived directories now carry a licence or governance statement:

| directory | statement |
|---|---|
| `Archive/lao-dataset/` | public and redistributable (plan §4) |
| `Archive/sibling-datasets/` | public and redistributable, same terms |
| `Archive/lao-population/` | CC BY 4.0 |
| `Archive/case-source-material/` | **Creative Commons — human-set, 2026-09-05** |
| `Archive/plan-as-delivered/` | **Creative Commons — human-set, 2026-09-05** |

The last two had no statement, and they hold documents that are the human's and unpublished:
the manuscript this project is the worked case for, the TrustAgentic proposal and its
supplement, and the plan as delivered. `/release` forbids publishing a subset and mentioning
it afterwards, so this was the release's real blocker, and it was put to the human rather than
assumed. Both provenance files now record the answer.

### Personal information that is not a credential

**One third-party e-mail address, already public.** `knut.rand@dhis2.org` appears in 29
tracked files, all of them `service_info.json` — the reference model's own published
metadata, which the project records verbatim as the provenance of the model it is measured
against. It is that model's published contact address, and carrying it is closer to
attribution than to disclosure. Kept.

**One of the human's own**, in a markdown conversion of their own published 2013 article.

**The home-directory path, 3 965 occurrences in 348 files** — and this splits in two.
**3 927 are in `.log` files**, which record the commands that were actually issued, and those
commands did contain absolute paths because the driver constructs them. Writing `~` into a log
would be writing down a command that was not the command run; it would also edit files the
agent produced, invalidate 31 `.sha256` manifests and 113 recorded digests, and make the next
clean-room report 348 spurious differences. They stay, as a recorded decision (plan §4b).

**Two of the remaining twelve were in source code and are fixed.** `run_cleanroom.sh` and
`cleanroom_compare.py` each named this machine's repository path as a constant, so the one
harness a reader would most want to re-run only ran here. Both now derive it from the script's
own location. **No tracked script carries the path.** That was a portability defect rather
than a disclosure, and the scan is what found it.

## The assembly

The release is the repository. Rule 10 says the release is the whole tree, alternatives
included, so nothing is staged into a separate directory: a second copy of 2.6 GB is a second
thing to keep in step with the first.

Every item Rule 10 names is present and tracked:

- the data, all of it redistributable;
- every script, and `analysis/` entire;
- the environment at all three layers — the declarative spec, `lock.txt`, and the Dockerfile;
- the claim collection and the manuscript's provenance sidecar;
- the provenance records;
- **the instruction files and the skills**, because they determine how the analysis was
  produced and two runs under different instructions are two different methods;
- the hierarchical report and the reproducibility report;
- `analysis/run.sh`, which rebuilds everything.

**The paths not taken: 23 across 17 forks, and all 23 have an entry point.** Rule 10 calls
them the most valuable thing in the release, so they are counted rather than assumed — an
alternative nobody can run is a directory and not a path.

**What is deliberately not in it**, and why, is in `release_manifest.json`: the generated
hierarchical report (rebuilt in three seconds), chap-core's ~20 GB of per-split working
directories, the built environment, and the working-tree half of the holdout seal — which is
unversioned on purpose, because a versioned seal seals every clone and turns a reproduction of
phase E into a description of one.

## The checks the release rests on

| check | when | outcome |
|---|---|---|
| `/validate invariants` | every commit | **all ten hold** |
| `/validate cleanroom` | 2026-09-05 | **`analysis/run.sh` exited 0 from a clean checkout**, 14.87 h, with `06_external` in the tree; 207 of 207 scores from our models identical |
| `/validate outsider` | 2026-09-05 | ran, **found seven things**, one of which is not yet fixed; **one of its two agents was killed by an account spend limit and the write-into-the-tree half did not run** |
| `/hierarchical-report` | 2026-09-05 | rebuilt, 69 combinations, 1 387 pages |
| `/repro-report` | 2026-09-05 | written, with ten entries under *what does not hold* |

## What is not cleared, and why the push is not in this batch

**One defect found by the outsider check is unfixed and is in the tree.**
`01_weighting/a_equal/scripts/choose_weighting.py` records a six-member pool where four ran,
in 40 of 47 combinations, because it builds its statement of the pool from an unfiltered glob.
No score moves, and the registered prediction the node exists to make is written on a premise
the file itself contradicts. **A release must not claim more than its checks support**, and
this one currently would. It is **batch 32**, and its defence is built against the clean-room
run's own output, as the previous four fixes of this family each were.

**The push is batch 33.** Both of the human's answers are recorded, so batch 32's fix is its
only remaining blocker. The remote — `github.com/sandvelab/veridical-agentic-dengue-laos`,
human-set 2026-08-31 — does not exist and will be created as the last step, after the scan,
which has now run.

**Feasibility, measured**: `.git` is 131 MB packed and no tracked file exceeds 50 MB, though
the working tree is 2.6 GB.

---

**Agency:** agent-autonomous for the scan, the assembly and this reading. The licence answer
and the repository name are human-set; the decision that the push waits for batch 32 is the
agent's, on the standing rule that a release must not claim more than its checks support.
