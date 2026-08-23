# reconnaissance

Scripts that establish facts about an external system this project depends on but does not
control. They are machinery rather than analysis: nothing here answers a claim in
`analysis/`, and no number from here reaches the manuscript. What they produce is the
evidence behind a batch report.

They live outside the claim tree deliberately. The tree holds the analysis of dengue
incidence in Laos; "what does `chap eval` actually compute" is a question about the
instrument, not about the disease, and giving it a node would put a fact about the platform
on the same footing as a finding about the data.

| Script | What it establishes |
|---|---|
| `capture_chap_surface.sh` | The installed `chap-core`'s CLI surface, and one end-to-end `chap eval` smoke run on a pinned example dataset and a pinned example model |
| `describe_evaluation.py` | What a Chap evaluation `.nc` contains, and the CRPS behind it at global, per-region, per-split and per-cell resolution — computed with chap-core's own metric classes, never reimplemented |

Both write to `AI-generated/chap-reconnaissance/`, which carries a `provenance.md` naming
the commit, the pins and the invocation for every file. Re-running either script rebuilds
its outputs.

Invoke from the repository root:

```bash
bash AI-internal/reconnaissance/capture_chap_surface.sh
```
