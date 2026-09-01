# AI-internal

The machinery: the scripts the skills call, the reference material the thin skills defer to,
and the log of what has been done.

| Path | Holds |
|---|---|
| `useful-scripts/` | The repository's own machinery — the scripts the skills call, and the checks on them. **What is in it is listed in its own `README.md`**, with one row per script; a second list here would go stale the first time a batch adds one, which it had |
| `skill-references/` | The exact commands, formats and edge cases the skills defer to |
| `reconnaissance/` | Scripts that establish facts about external systems the project depends on but does not control |
| `vertical-slice/` | The scripts of batch 6. The persistence model itself was **moved into the claim tree by batch 7**, with its history, so it is no longer here |
| `data-acquisition/` | Scripts that bring external data into `Archive/`. One-off: once a file is archived and committed, the repository reproduces without network access |
| `ai_task_history.md` | One line per completed task, `T1`, `T2`, … |
| `ai_task_details.md` | The expanded entry for each |

The task log is **part of the published record** of how the work came about, not a private
working note. Write entries a reader who was not present can follow, and keep them honest
about what did not work.
