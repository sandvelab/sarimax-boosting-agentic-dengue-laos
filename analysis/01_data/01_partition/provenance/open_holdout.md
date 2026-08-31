# Provenance — opening the seal, and the file phase E evaluates on

```
result:              results/phase_e_1998-01_2010-12.csv
                     results/phase_e_opening.json
                     results/phase_e_outputs.sha256
script:              scripts/open_holdout.py
                     sha256:90277c52b5943eafab8bff2d7416959e5662e3ac274cea7b15890530d3806188
invocation:          "$PYTHON" scripts/open_holdout.py
                     (from the node directory, via run.sh; PYTHON is
                     environment/chapenv/bin/python)
inputs:              analysis/01_data/01_partition/results/development_1998-01_2009-12.csv
                     sha256:c9bf8b0849c768bfe6c65d54975dd08fa390204f8b59e76904170222a7a87d4c
                     analysis/01_data/01_partition/results/holdout_2010_SEALED.csv
                     sha256:e6d576431023b877432ca55e0dc93daeb020fac0fd4aaf71867bbc9f0849f073
                     Archive/lao-dataset/chap_LAO_admin1_monthly.csv
                     sha256:19488aa1fc4d961ae1a6aeb75b874789576877664fce47713628f497a06fff56
                     (read for its line order, and to verify the assembly against it)
environment:         environment/ (project main) — CPython 3.13.0, chap-core==2.1.0
seeds:               none. The assembly is a deterministic re-ordering of lines already on
                     disk; project seed 20260822 has no surface here.
commit:              895a9f8
instructions-commit: cf97b81 (AGENTS.md, CLAUDE.md, .claude/)
node:                analysis/01_data/01_partition
produced:            2026-08-31
alternatives-considered: point `02_setup` at `Archive/lao-dataset/` directly for holdout
                     combinations, and skip this file. Rejected on two grounds. The archive
                     is `(IS_SHADOW)` material with its own checksum manifest, and a setup
                     stage reaching into it would put the read outside the tree, where no
                     node's provenance covers it. And the licence to read the whole record
                     belongs to this node because this node is where the proof lives that
                     the two parts partition the source exactly — which is the fact that
                     makes putting them back together legitimate rather than a second
                     import of the data.
                     Also considered: write the file at batch 5's design time and leave it
                     unread until phase E. Rejected because a file on disk is a file
                     something can read, and the seal is cheaper to keep when the artefact
                     does not exist.
agency:              agent-autonomous. That the holdout is opened once, in one batch, for
                     the final validation is human-set (plan §3, readme "What must not
                     happen" 1). How it is opened — here, from the two parts, verified
                     against the archive — is this batch's.
```

**What it establishes.** The file phase E evaluates on is the archived source again, byte for
byte: 2 808 data rows, 2 592 from the development file and 216 from the sealed one, in the
source's own order, and `byte_identical_to_archived_source` is true in
`results/phase_e_opening.json`. Nothing is re-derived from the raw data and nothing about
2010 is summarised — the assembly is on lines and the verification is on hashes.

**Why the order is taken from the source rather than by concatenation.** The same reason
`partition_dataset.py` checks content and order separately: the file is ordered by province
and then by month, so the holdout is not a suffix of it. Concatenating the two parts would
produce a file with the same rows in a different order, and a rolling backtest reads order.
Taking each line from the source in the source's sequence makes the result the archive again
rather than a re-sorted copy of it.

**What this file being on disk means for the seal.** It means the seal is open. Plan §3
allows exactly one opening and this is it; the evidence that it happened here and not
earlier is that no `analysis/results/*__holdout/` directory exists at any commit before
895a9f8, and that the set evaluated on it was frozen and committed in batch 15, before this
script existed. The development file is unchanged and every development result still reads
it: which of the two a combination faces is decided by `analysis/scripts/lib/combos.py`
from the `__holdout` suffix, and by nothing else.
