# Provenance — the two sibling datasets, cut onto the Lao calendar

```
result:              results/THA_development_1998-01_2009-12.csv
                     results/THA_full_1998-01_2010-12.csv
                     results/VNM_development_1998-01_2009-12.csv
                     results/VNM_full_1998-01_2010-12.csv
                     results/part_structure.csv
                     results/schema_reconciliation.json
                     results/sibling_partition_check.json
                     results/sibling_outputs.sha256
script:              scripts/partition_siblings.py
                     sha256:776c18c2096709126524b7d4b92ca8abc075fbab7c81cb3b44e3cf1caae0f89e
invocation:          "$PYTHON" scripts/partition_siblings.py
                     (from the node directory, via run.sh; PYTHON is
                     environment/chapenv/bin/python)
inputs:              Archive/sibling-datasets/tha/chap_THA_admin1_monthly.csv
                     sha256:423d8b73b6e42bc90db8fea2db77463af77f8c30b6b02b66825acd51b83a1e42
                     Archive/sibling-datasets/vnm/chap_VNM_admin1_monthly.csv
                     sha256:a36ac87b936bd8ceee8d47eaeb798aae4988b4bfb921d68970096c534ae9b919
                     Archive/sibling-datasets/tha/chap_THA_admin1_monthly_schema.json
                     sha256:65666180c84f774d1c285de3a71a63c37701124439cc9dcac4b7f56662ae6b97
                     Archive/sibling-datasets/vnm/chap_VNM_admin1_monthly_schema.json
                     sha256:6ffa19e0a6c0b543d9e1801c3dfa1f2086e72df0adef89bd346d184857971e2a
                     Archive/sibling-datasets/sha256sums.txt (re-verified at run time)
                     analysis/01_data/01_partition/results/development_1998-01_2009-12.csv
                     sha256:c9bf8b0849c768bfe6c65d54975dd08fa390204f8b59e76904170222a7a87d4c
                     analysis/01_data/01_partition/results/phase_e_1998-01_2010-12.csv
                     sha256:19488aa1fc4d961ae1a6aeb75b874789576877664fce47713628f497a06fff56
                     (the last two only for their period spans: "the same calendar" is what
                     those two files are, so the bounds are read off them rather than
                     repeated here as constants)
environment:         environment/ (project main) — CPython 3.13.0, chap-core==2.1.0
seeds:               none. Every cut is a deterministic filter on time_period and the
                     structural summaries are counts; project seed 20260822 has no surface.
commit:              bfbc096
instructions-commit: 595c32d (AGENTS.md, CLAUDE.md, .claude/)
node:                analysis/01_data/03_siblings
produced:            2026-09-04
alternatives-considered: running Thailand on its own calendar, 1993-01 to 2022-12, which
                     would have given a longer training record and a final year of 2022.
                     Rejected: the external check asks whether the Lao result holds in
                     another place, and a country evaluated on different months differs
                     from Laos in two ways at once. Thailand's other twenty-two years are
                     the material for a different question — whether 2010 in particular was
                     hard — and this batch leaves them unspent, which is a decision and not
                     an oversight.
agency:              agent-autonomous. That these two datasets are the external check is the
                     plan's (human-set, §4, confirmed 2026-08-31); the calendar, the two
                     arrangements and everything below are the agent's.
```

**What it establishes.** Each country's two parts are exact subsets of its source, sharing
its header, with no row invented, duplicated or lost inside the window, and the development
part a strict subset of the full part whose complement is exactly the final year. Thailand
gives 11 088 and 12 012 rows over 77 provinces; Vietnam 9 072 and 9 828 over 63. Vietnam's
source already runs 1998-01 to 2010-12, so its full part is its source; Thailand's is cut
from 27 720 rows.

**What the schemas claim, against the files.** Two of the three statements batch 3 found not
to describe the Lao file describe none of the three, so they are the harmonisation's rather
than Laos's.

- `rainfall` is declared in all three as a monthly total in millimetres and is a **mean
  daily rate** in all three: summing the monthly values over a year gives 23–107 mm, and
  multiplying by the days in a month puts the same years at roughly 1 500–2 000 mm.
- `row_count` **means different things in different files of one harmonisation.** Vietnam
  declares 9 612 against 9 828 rows and Laos 2 575 against 2 808 — both the count of rows
  with an observed target. Thailand declares 27 720, which is its row count exactly, and
  696 more than its complete records.
- **Thailand's `population` is not a static snapshot.** Its schema describes annual WorldPop
  values interpolated between the 2000, 2010 and 2020 anchors, and all 77 provinces carry a
  varying series. Vietnam and Laos ship one constant per province. The fork this project
  spent a node arguing over is one the harmonisation itself answers differently per country.

**Why nothing here is sealed.** Plan §3 seals the Lao 2010 because the model was developed
against Lao 1998–2009 and a leak would have made the headline a lie. No model is developed
on these files: the external check runs the model the tree already reports, at the
configuration it already has. There is nothing here for a year to leak into, so sealing
would have been a ceremony rather than a protection, and the batch says so rather than
performing it.
