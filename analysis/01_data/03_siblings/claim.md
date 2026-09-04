# Claim

What do the two sibling harmonised datasets — Thailand and Vietnam — contain, and on what
arrangement of them can the reported model be checked so that the comparison with Laos is
about the country rather than about the years?

The plan's §4 names `tha` and `vnm` as an external check and nothing more: no model is
developed on them, so nothing here is sealed and neither file is a holdout. What this node
has to settle is the arrangement, because an external check run on a different span would
confound the country with the calendar, and then it would answer neither question.

## Children

kind: -
main-path: -

## Environment

inherits: the project main environment (`environment/`)

## Decisions taken here

| Decision | Basis | Agency |
|---|---|---|
| **Thailand is truncated to the Lao calendar, 1998-01 to 2010-12** | Its file runs 1993-01 to 2022-12. The external check asks whether the Lao result holds in another *place*; holding the years fixed is what makes the country the only thing that varies. Thailand's other twenty-two years answer a different question — whether 2010 in particular was hard — and are left unspent | agent-autonomous |
| **The two arrangements mirror Laos exactly: 3/8/3 on 1998-01..2009-12, and 3/4/3 on the full file** | Batch 3 fixed both schemes and said a horizon changed midway makes every earlier number incomparable. Re-choosing them for the siblings would have made the external check a different analysis rather than the same one on other data | agent-autonomous |
| **No sibling year is sealed** | Plan §3's seal exists because the model was developed against Lao 1998–2009 and a leak would have made the headline a lie. The check runs the model the tree already reports, at the configuration it already has, so there is nothing here for a year to leak into. Sealing it anyway would have been a ceremony rather than a protection | agent-autonomous |

## Answers

_(What this node's analysis yielded. Each answer belongs in the claim collection
under `Human-AI-collaboration/claims/` with a pointer to the result grounding it.)_

**The mirror is exact on all three countries.** Applied to the sibling files, the two Lao
schemes evaluate **2008-01 to 2009-12** and **exactly 2010**, from training sets ending
2007-12 and 2009-12 — the same months Laos is scored on, checked against chap-core's own
splitter rather than against the formula in its docstring. Thailand contributes 76 of its
77 provinces (its filter drops TH-38, which never reports) over 1 824 and 912 cells;
Vietnam contributes all 63 over 1 512 and 756. Laos contributes 16 over 371 and 192.
→ `results/backtest_scheme_external.json`, `split_schedule_external.csv`

**Two of the three things the Lao schema got wrong are the harmonisation's and not the Lao
file's.** `rainfall`, declared in all three schemas as a monthly total in millimetres, is a
mean daily rate in all three: summing the monthly values over a year gives 23–107 mm, and
multiplying by the days in a month puts the same years at roughly 1 500–2 000 mm. And
`row_count` does not mean the same thing in the three files — Vietnam declares 9 612
against 9 828 rows and Laos 2 575 against 2 808, both counting rows with an observed
target, while Thailand declares 27 720, which is its row count exactly and 696 more than
its complete records.
→ `results/schema_reconciliation.json`

**The fork this project spent a node arguing over, the harmonisation answers differently
per country.** `02_setup/01_population` chose between the archived static population column
and a series back-cast from published growth. Thailand ships the second: all 77 provinces
carry annual WorldPop values interpolated between the 2000, 2010 and 2020 anchors. Vietnam
and Laos ship the first.
→ `results/schema_reconciliation.json`
