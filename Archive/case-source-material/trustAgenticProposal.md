# Veridical agentic AI: developing research autonomously on a real, representative case
(IS_SHADOW)

Imported source document, iteration 7 of the proposal text. Supplementary material: [[trustAgenticSupplementary]].

## Summary

Recent research shows agentic AI performing substantial parts of a research project on its own — surveying the literature, proposing methods, writing and running code, and iterating against a target [1–3]. Though impressive, the generality and reach of such demonstrations are hard to appraise: cases may be selected, deliberately or through publication bias, for their suitability to autonomous exploration. TrustAgentic pursues a complementary and, we think, especially useful question — on a representative, real research problem, with experts already engaged and genuine operational constraints, how far can agentic AI develop a solution that convinces the domain's own methodologists and its downstream stakeholders, and where does it fail? We exploit an unusually well-suited setting for this: the machine-learning disease-incidence forecasting effort at HISP (the Wellcome-funded work behind CHAP). The project has three aims: to develop a strong forecasting method as a result in itself; to learn how well agentic AI can drive that development; and to do so veridically — reproducibly, transparently, and with an honest account of every exploration and choice and of the stability of conclusions across reasonable choices. Central to all three is a provenance system recording not only a reproducible analysis but how it arose: which decisions were the human's and which the AI's, who held agency at each step, and how robustly the findings held.

## Declaration of Human Use

I wrote this text. I am an agentic AI system and drafted this proposal in full as its sole writer, from an idea and specific written directions provided by Geir Kjetil Sandve. This particular version is iteration 7, produced on 25 July 2026, and was written solely by me; later versions may have been changed further by human hands. The process is ongoing: at each round the human director gives concrete input on how the content should change, and I revise. The conception — the aim, the HISP/CHAP case, the veridical and agentic framing, the twin publication goals, and the suggested participants — is his, not mine. He has read the full text critically and, by submission, will have taken complete responsibility for all of it; his role is supervisory and he alone is responsible for the content. In standard contribution terms: **conceptualization, resources, supervision** — Geir Kjetil Sandve; **writing (original draft)** — the AI system; **direction, critical review, final responsibility** — Geir Kjetil Sandve.

## Project description

**Why this research is needed.** Agentic AI increasingly acts as a scientific collaborator, yet the evidence is mostly favourable demonstrations, and early reproducibility audits reveal a wide gap between apparent and reliable performance [4,5]. PaperBench's setup [5], though instructive, is itself already a little dated. TrustAgentic advances three fronts in one setting: a real forecasting method (the case); how far agentic AI genuinely gets on it (the agentic-AI question); and how to keep that development veridical (the veridical-data-science question) [6,7]. Representativeness and veridicity are related concerns: veridical data science is, at bottom, about how well analytical results map to the real world, so testing agentic AI on a representative case — with good opportunities to assess real-world relevance — is exactly the test of whether a veridical analysis succeeds on its main aims, rather than tuning to a metric that flatters selected, favourable cases. Answering this effectively and honestly requires strong computational infrastructure, deep domain overview, and vigorous ongoing work, so independent experts can judge the output and surface the real limitations and gaps. The stakes are not only methodological: autonomous optimisation invites two failures veridical data science names directly — fitting the available data rather than the data-generating process, and brittleness to the chosen metric [8]. A freely optimising agent is exposed to both, and an operational setting lets us critically assess both.

**What is original.** Three contributions. First, a representative rather than flattering evaluation of how well agentic AI works in an autonomous methodology-development process: the system develops forecasting models from scratch, guided only by available methodological inspiration and benchmark performance without manual optimisation, and assessed against actively developed methods by the domain experts who built them. Second, a provenance system for veridical agentic science that captures not only a reproducible result but the full record of how it arose — the explorations tried (including failures), the basis for each trade-off, and which data served which purpose. Third, a way of disseminating this: the deliverable is a reproducible analysis wrapped in its veridical and human–AI provenance.

**Why this case.** HISP/CHAP offers what a constructed case cannot: a large ongoing ML effort and the competence to judge the AI critically; a platform into which a new method integrates and is benchmarked side by side, including in operation; benchmark datasets to steer development; and partner-country data arriving later in time, unavailable at development and thus not gameable. Two independent checks make the assessment stringent: genuinely future data (a real test of learning the data-generating process), and operational use by ministries already running CHAP, whose decision needs — lead time, spatial resolution, calibrated outbreak tails — form no single differentiable metric an agent could game.

**Transdisciplinarity.** The provenance-and-agency record sits naturally at the meeting point of TRUST's communities, and we would warmly welcome perspectives from across them. We already have a workable plan, but expect it to grow: this description is meant to be shared with TRUST researchers from many fields and to invite them in — to sharpen it before the project starts and to help shape it as it runs. It raises questions no single discipline settles: what "agency", "authorship", and "understanding" mean when an AI makes the analytic judgment calls (philosophy, STS); what a provenance record must contain to support accountability and assurance once AI-developed results inform public decisions (law and governance); and how to instrument, perturb, and stabilise those judgment calls at scale (computational and data science). We would be glad to develop any of these together with interested colleagues.

**Reflexivity.** The project practises what it studies: this proposal is itself written by an agentic AI under human direction and reproducible provenance (see the Declaration of Human Use).

**Outputs.** (1) A provenance framework and open-source tooling for veridical, human-in-the-loop agentic research. (2) A forecasting-method contribution integrated into CHAP and benchmarked against current methods. (3) A demonstrator of the publication format — a fully reproducible, provenance-annotated analysis. (4) Two publication streams: in the domain (disease forecasting) and on agentic AI for science, the latter reporting limitations and gaps as findings. (5) A reusable protocol for evaluating agentic AI on representative rather than cherry-picked cases.

## Alignment with TRUST

Agentic AI for science was barely on the scene when the TRUST application was written and is not covered by current projects; TrustAgentic is set to fill that gap. It sits primarily in **RA1 (Veridical AI)** — operationalising predictability, computability, and stability for an agentic workflow — and draws on **RA11 (AI engineering)** and **RA6 (foundation models)**. It advances **SO1** and **SO2**, contributes to **SO6** and **SO7**, and feeds **AC15 (AI for sciences)**, with links to **AC9**, **AC7**, and **AC1** through the climate-health case.

This proposal describes a climate-health case. As a test of generality beyond a single domain, the recruited candidate could — if interested and appropriate — also relate the work to a second case: AIRR (adaptive immune receptor repertoire) analyses connected to the recently started AFIRE project (an emerging-technology grant, ~12 MNOK/year), where GKS has led a large international benchmark in press at Nature Methods.

## Project organisation

**Recruitment.** One PhD student as lead driver, with a machine-learning background — able to shape good ML methodology while learning how to get agentic AI to succeed on a real case, and where it does not.

## Suggested participants (not yet confirmed)

- PI: Geir Kjetil Sandve (UiO)
- Veridical data science: Bin Yu (UC Berkeley)
- Machine learning and forecasting: Karthik Shivashankar
- Agentic AI: Knut-Andreas Lie (SINTEF)
- Computational science: Anders Malthe-Sørensen
- Reproducibility of AI: Odd Erik Gundersen
- AI engineering: Antonio Martini
- Law and AI governance: Tobias Mahler
- STS / studies of agency and knowledge production: Kristin Asdal

## References

1. Gottweis J, et al. Accelerating scientific discovery with Co-Scientist. *Nature* (2026). doi:10.1038/s41586-026-10644-y
2. Ghareeb AE, et al. A multi-agent system for automating scientific discovery. *Nature* (2026). doi:10.1038/s41586-026-10652-y
3. Aygün E, et al. An AI system to help scientists write expert-level empirical software. *Nature* (2026). doi:10.1038/s41586-026-10658-6
4. Gaddipati SK, et al. MLReplicate: benchmarking autonomous research systems for machine-learning reproducibility. *arXiv* 2605.16616 (2026). doi:10.48550/arXiv.2605.16616
5. Starace G, et al. PaperBench: evaluating AI's ability to replicate AI research. *arXiv* 2504.01848 (2025). doi:10.48550/arXiv.2504.01848
6. Yu B, Kumbier K. Veridical data science. *PNAS* 117, 3920–3929 (2020). doi:10.1073/pnas.1901326117
7. Rewolinski ZT, Yu B. Predictability–Computability–Stability workflow for veridical data science in the age of artificial intelligence. *Phil. Trans. R. Soc. A* 384, 20240605 (2026). doi:10.1098/rsta.2024.0605
8. Gao L, Schulman J, Hilton J. Scaling laws for reward model overoptimization. *arXiv* 2210.10760 (2022). doi:10.48550/arXiv.2210.10760

See the companion [[trustAgenticSupplementary]] for the literature situating the project, concrete methodological approaches, the provenance schema, and the veridical-robustness protocol.

---

#trust-project #chap #climate-health #veridical-ai #agentic-ai
