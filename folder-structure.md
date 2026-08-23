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
│   └── NN_name/            child nodes, same shape, recursively
├── environment/            the one main environment (spec · build · lockfile · image)
├── Archive/                imported source material, never edited, (IS_SHADOW)
├── AI-generated/           derived documents — regenerable, therefore deletable
│   ├── batch-reports/      one per executed batch — the exception: not regenerable
│   ├── chap-reconnaissance/  what the pinned platform is and does
│   ├── hierarchical-report/
│   └── reproducibility-report/
├── AI-internal/
│   ├── useful-scripts/     node.py · check_invariants.py · claims.py · build_hierarchical_report.py
│   ├── reconnaissance/     facts about external systems the project does not control
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
| `Archive/` | Read-only. Marked `(IS_SHADOW)` on line 2. Anything needing change is copied out first. |
| `AI-generated/` | Everything here is rebuilt by a recorded recipe. Never hand-edit; if it is wrong, its source is wrong. |
| `AI-internal/` | The machinery. Scripts have a dual API/CLI interface. |
| `Human-input/` | Mine. You execute plans from here; you do not rewrite them except to add output links. |
| `Human-AI-collaboration/claims/` | The only route from results to text. |
| `Human-AI-collaboration/manuscript/` | Downstream of claims, never upstream. |

## Node directories

Named `NN_shortName`, numbered in the order the parent runs them. Each holds `claim.md`,
`run.sh`, `scripts/`, `results/`, `provenance/`, and `env/` only where it overrides the main
environment.
