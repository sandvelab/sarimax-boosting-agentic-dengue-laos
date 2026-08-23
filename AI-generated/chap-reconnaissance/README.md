# chap-reconnaissance

What the installed Chap platform actually is and does, captured to files during batch 2 so
that `26-08-23_b02_chapSetup.md` quotes stored output rather than terminal scrollback. This
is `AGENTS.md` §1 applied to reconnaissance: a fact established only in an agent's context
has no provenance, and the fact that it is a fact about a tool rather than about the data
does not change that.

Everything here is regenerable — rebuild it with
`bash AI-internal/reconnaissance/capture_chap_surface.sh` — and `provenance.md` records the
commit, the pins and the invocation behind each file.

| File | What it holds |
|---|---|
| `chap_version.txt`, `chap_help.txt`, `chap_eval_help.txt`, `chap_export_metrics_help.txt` | The CLI surface of `chap-core` 2.1.0 as installed |
| `chap_test.txt` | `chap test`, the platform's own self-diagnostic |
| `chap_metrics_registry.csv` | Every metric the platform can compute, with its aggregation operation |
| `smoke_eval.log`, `smoke_eval.nc` | One end-to-end backtest: 5 regions, monthly, 3 periods × 4 splits, on a pinned example dataset and a pinned example model |
| `smoke_eval_structure.txt` | The dimensions, variables and attributes of that `.nc` |
| `smoke_metrics_aggregate.csv` | What `chap export-metrics` gives: one row per evaluation, all metrics, no breakdown |
| `smoke_crps_global.csv`, `smoke_crps_by_location.csv`, `smoke_crps_by_split.csv`, `smoke_crps_detailed.csv` | The same CRPS at four resolutions, recovered from the `.nc` with chap-core's own metric classes |
| `smoke_samples_per_cell.csv` | How many forecast samples each cell carries — one, for this deliberately trivial model |
| `smoke_inputs.sha256` | The hash of the example dataset and the commit of the example model |
| `smoke-work/` | Untracked. The fetched inputs and the ~200 MB environment chap-core builds for the example model. |

**None of these numbers is a result of this project.** They come from an unrelated example
dataset and a linear regression that emits a single sample, and they exist only to show
that the chain runs and to expose the shape of what it produces.
