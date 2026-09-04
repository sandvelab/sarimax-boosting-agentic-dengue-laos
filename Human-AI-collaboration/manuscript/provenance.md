# Provenance — manuscript

One section per document. Append; never overwrite an existing section.

---

## `26-09-05_illustratingCase.md` and `26-09-05_illustratingCase_sidecar.md` — 2026-09-05

```
generated from:      Human-input/Plans for AI generation/26-08-22_dengueForecastingCase.md
                     iteration 19 (batch 19, phase E)
written from:        Human-AI-collaboration/claims/claims.md — 47 claims, C1..C47
                     each of which names the stored result grounding it
route:               Rule 9's two steps. Results -> claims -> text. No figure in the
                     write-up was read from a result file directly; every one of them was
                     read from a claim, and the claim from the result.
sidecar:             26-09-05_illustratingCase_sidecar.md — every passage mapped to the
                     claims it rests on, or to what kind of statement it is instead
                     (design, record, judgment) where it rests on none
audited by:          .venv/bin/python AI-internal/useful-scripts/claims.py check-text
                     Human-AI-collaboration/manuscript/26-09-05_illustratingCase.md
                     51 sentences flagged; every one carrying a figure was checked by hand
                     and is in the sidecar. The matcher is deliberately crude and flags
                     prose that asserts nothing about the analysis.
commit:              (batch 19's closing commit)
instructions-commit: 595c32d (AGENTS.md, CLAUDE.md, .claude/)
produced:            2026-09-05
```

**What it is for.** The manuscript this project is the worked case for
(`Archive/case-source-material/reproAgenticAiManuscript.md`) has an *An illustrating case*
section marked *to be written later*, and an Appendix specifying a different case — a
genomic region-set co-occurrence analysis — with a worked claim-tree skeleton and a
perturbation space. **This case replaces that one** (human-set, 2026-08-23), so the write-up
supplies both: the section, and what the Appendix supplied for the case it replaces, in
dengue terms. The archived manuscript stays stale by design, because `Archive/` is never
edited.

**Three kinds of statement, kept apart in the sidecar.** *Design* statements describe how the
project was set up and are grounded in the plan and `AGENTS.md`. *Record* statements describe
the project's own history and are grounded in the batch reports and validation records.
*Judgment* is the agent's opinion, and the section that is entirely judgment says so at its
head.

**Agency.** `agent-autonomous` throughout, including the judgment about where the setup was
more trouble than it was worth. The human delegated that judgment on 2026-08-31 and reads it
afterwards; recording it as jointly held because they read it would overstate their part
(plan §4b). If a later edit changes what a sentence says rather than how it says it, that
sentence becomes `agent-on-human-assessment` and the change is logged in the plan's §4b.

**Two statements deliberately rest on no claim and say so in their own text**: that three
countries of one harmonisation are not a sample, and that the development-arrangement gap
between Laos and the siblings is not attributable to optimisation alone. Both are limits on
what the claims support rather than findings, and they are carried in the scope fields of
C42 and C43.
