# Folder structure

What each directory is for, and the one rule that governs it. Create every folder with a
`README.md` at the same time.

```
<repo>/
├── readme-at-start.md      what THIS project is           read first, every session
├── README.md               what is here
├── MOTIVATION.md           why the repository is shaped this way
├── AGENTS.md               the standing instructions       part of the method
├── CLAUDE.md               pointer to AGENTS.md
├── .claude/
│   ├── settings.json
│   └── commands/           the 17 skills
├── analysis/               THE CLAIM TREE — the project itself
│   ├── claim.md            the top-level analytical aim
│   ├── run.sh              reproduces the entire reported analysis
│   ├── scripts/  results/  provenance/
│   ├── NN_name/            sub-analyses children — numbered, every one of them runs
│   └── a_name/             alternatives children — lettered, only the main path runs
│                           (every node below 01_data reads and writes results/$COMBO/,
│                            which defaults to `main`)
├── environment/            the one main environment (spec · build · lockfile · image)
├── Archive/                imported source material and data, never edited
│   ├── case-source-material/  the five documents the project starts from, (IS_SHADOW)
│   ├── lao-dataset/        the data, pinned by commit, with a checksum manifest
│   ├── lao-population/     the annual national series the population fork back-casts from
│   ├── sibling-datasets/   Thailand and Vietnam, same commit — the external check's data
│   └── plan-as-delivered/  the plan before any of it had been run
├── AI-generated/           derived documents — regenerable, therefore deletable
│   ├── batch-reports/      one per executed batch — the exception: not regenerable
│   ├── chap-reconnaissance/  what the pinned platform is and does
│   ├── method-reconnaissance/  what the reference model scores and costs, and what else the library holds
│   ├── vertical-slice/     the first model end to end, before the tree existed
│   ├── validation/         what /validate cleanroom and /validate outsider found
│   ├── determinism-checks/ Rule 6: our models run twice and diffed
│   ├── hierarchical-report/
│   └── reproducibility-report/
├── AI-internal/
│   ├── useful-scripts/     node.py · check_invariants.py · claims.py ·
│   │                       build_hierarchical_report.py · verify_model_determinism.sh
│   ├── reconnaissance/     facts about external systems the project does not control
│   ├── vertical-slice/     the scripts of batch 6; its model now lives in the tree
│   ├── data-acquisition/   scripts that bring external data into Archive/
│   ├── skill-references/   the detail the thin skills defer to
│   ├── ai_task_history.md
│   └── ai_task_details.md
├── Human-input/
│   └── Plans for AI generation/   plans executed by /do
└── Human-AI-collaboration/
    ├── claims/             claims.md — every statement bound to its result
    └── manuscript/         the article, written from the claims
```

## The rule for each

| Folder | Rule |
|---|---|
| `analysis/` | `run.sh` at the root reproduces everything. Alternatives stay in the tree. Never create nodes by hand — use `/node`. |
| `environment/` | One environment for the whole analysis. A node-level override must justify itself in that node's `claim.md`. |
| `Archive/` | Read-only and write-once. Text documents are marked `(IS_SHADOW)` on line 2; data files cannot be, because inserting a line would edit them and break their checksums, so their folder's `README.md` and `provenance.md` carry the statement instead. Anything needing change is copied out first. |
| `AI-generated/` | Everything here is rebuilt by a recorded recipe. Never hand-edit; if it is wrong, its source is wrong. |
| `AI-internal/` | The machinery. Scripts have a dual API/CLI interface. |
| `Human-input/` | Mine. You execute plans from here; you do not rewrite them except to add output links. |
| `Human-AI-collaboration/claims/` | The only route from results to text. |
| `Human-AI-collaboration/manuscript/` | Downstream of claims, never upstream. |

## Node directories

Named `NN_shortName`, numbered in the order the parent runs them. Each holds `claim.md`,
`run.sh`, `scripts/`, `results/`, `provenance/`, and `env/` only where it overrides the main
environment.
