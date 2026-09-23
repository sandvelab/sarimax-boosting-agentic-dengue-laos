# provenance — `manuscript/`

One section per document. Append; never overwrite an existing section.

---

## `26-09-22_twoStageDengueLaos.md`

generated-from: `Human-input/Plans for AI generation/26-09-20_sarimaxResidualBoostingCase.md`
        — iteration 1, produced at the human's request outside the batch sequence (ledger row
        17b; plan §4b, 2026-09-22). The plan's row 20 reserves the full manuscript for phase F;
        this is the short overview asked for once the held-out year was in.
produced: 2026-09-22
written-from: `Human-AI-collaboration/claims/claims.md`, claims C1–C20. Nothing was read from a
        result file while drafting: every figure in the draft is one a claim already states, and
        the claims carry the pointers to the results.
sidecar: `26-09-22_twoStageDengueLaos_claims.md` — every statement mapped to its claim, or, for
        design facts, to the stored file that fixes them.
covers: the development backtest (C1, C6–C13) and the held-out year (C14–C20), the central
        comparison on both, both required baselines on both, and the implications.
check-text: `/claims check-text` flags 12 sentences. Each was read. Ten are method statements or
        interpretive sentences whose numbers come from claims named in the sidecar — the check
        matches on shared content words and cannot see either. Two were genuinely absent from
        the sidecar when first run and were added. One factual error was found this way and
        corrected before the draft was committed: the ensemble was described as losing to "the
        simplest baseline in the study", where the baseline that beats it is seasonal
        climatology and the simplest is persistence, which it beats.
not-in-the-draft: the analysis-tree mechanics, the stability manifests' construction, the
        freeze and the opening procedure — they are in the batch reports and the node claims,
        and §7 points at them rather than restating them. The five tier-3 alternatives are named
        in §6 without their individual reasons; `manifest_holdout.csv` carries those.
agency: agent-autonomous (the drafting and the selection of what to include). The findings it
        reports rest on decisions recorded in the plan's §4b, of which the main path, the fixed
        stage 1 and the choice not to reopen it are human-set.
information: none retrieved; every input is a claim or a file already in this repository.

---

## `26-09-23_twoStageDengueLaosManuscript.md`

generated-from: `Human-input/Plans for AI generation/26-09-20_sarimaxResidualBoostingCase.md`
        — iteration 1, ledger row 20 (phase F, release): the full manuscript the plan reserved for
        that row. The short overview of 2026-09-22 stands beside it, unchanged.
produced: 2026-09-23
written-from: `Human-AI-collaboration/claims/claims.md`, all 32 claims (C1–C32). Method statements
        were read from the files the sidecar names — node `claim.md` files, `conclusion.json`
        files, the freeze and opening records, the plan's §4 and §4b — and from nothing else.
        No result file was read to obtain a number a claim does not already state.
literature: the introduction and discussion cite eight references. All eight come from the
        batch-10 literature record (`AI-generated/batch-reports/26-09-20_b10_stage2SystematicSecondIteration.md`
        §2), where they were retrieved and read during that batch. When this manuscript was written
        their bibliographic details were re-verified by web search (agent-retrieved, 2026-09-23),
        and the one whose characterisation in the record was loose — Sesay et al. (2026) — was
        checked against the article's abstract and corrected to it: the near-nominal calibration
        belongs to a negative-binomial integer autoregression against a negative-binomial GLM that
        under-covered, not to "a negative-binomial autoregression against a Gaussian model". The
        other seven papers were not re-read; the manuscript characterises them as the batch-10
        record does.
sidecar: `26-09-23_twoStageDengueLaosManuscript_claims.md`.
check-text: `/claims check-text` flags 77 sentences. Each was read. All are method statements,
        literature statements, interpretive sentences whose numbers come from claims named in the
        sidecar, reference-list fragments, or the agency statement — none carries a figure no claim
        states. One imprecision was found by reading them and corrected: the climate fields are read
        by the diagnostic node and by a row in each stability set as well as by candidates d and e,
        not by "one stability row" only.
length: about 7,100 words including tables and references.
not-in-the-draft: per-province and per-split tables (in the stability node's results and the
        hierarchical report); the individual reasons for the ten not-run holdout rows
        (`manifest_holdout.csv`); the mechanics of the freeze checks and the invariant checker.
decisions-taken-here (agent-autonomous, recorded in plan §4b, 2026-09-23): that the manuscript
        carries a section on the method of work (§3.9, and a paragraph of §5), because the plan's
        §1 makes the veridical record a deliverable of equal standing with the model; that its length
        and structure are those of a full research article with no venue's constraints applied, the
        target venue being undecided; that the agency statement (§8) is a section of the article.
agency: agent-autonomous (the drafting, the selection of what to include, the three decisions
        above). The findings it reports rest on decisions recorded in the plan's §4b, of which the
        architecture, the fixed stage 1, the pre-registration timing and the freeze decisions are
        human-set, and §8 lists them.
information: agent-retrieved (the reference re-verification and the Sesay abstract); otherwise
        every input is a claim or a file already in this repository.
