# TrustAgentic — Supplementary material
(IS_SHADOW)

Companion to [[trustAgenticProposal]].

The two-page main text is deliberately terse and assumes a knowledgeable reader; this supplement carries the background, concrete methods, and definitions a reader may want. Main-text references [1]–[8] are repeated here (§S5) alongside the fuller list.

## S1. Where the project sits in the literature

**Agentic AI for science — demonstrations and audits.** 2026 saw the first end-to-end agentic "AI scientist" systems reach leading journals: the Co-Scientist multi-agent system [1]; a multi-agent system for automating scientific discovery [2]; and a system that writes expert-level empirical software for scientists [3]. Even these already rest on a generation of agentic AI now being superseded. The counter-literature matters as much: reproducibility audits such as **MLReplicate** [4] and **PaperBench** [5] — an instructive if already somewhat dated setup — find a wide gap between apparent and reliable performance, and that no current framework completes a full research cycle dependably. TrustAgentic's distinctive move is to run this evaluation on a *representative* case, with independent domain experts and genuinely future data, rather than on a self-contained benchmark.

**Veridical data science (VDS).** The honesty criteria come from Yu & Kumbier's veridical-data-science programme [6] and its **Predictability–Computability–Stability (PCS)** workflow [7]. Predictability is the reality check — a model earns trust by predicting genuinely held-out data; computability covers the reproducible-compute life cycle; stability generalises uncertainty to the *judgment calls* made throughout an analysis (data cleaning, algorithm and hyperparameter choices). PCS maps almost exactly onto what an autonomous agent threatens, because the agent makes those judgment calls silently and at speed. The central VDS point for this project: relevance to the real world is the object of study, which is why a representative, operationally embedded case is the right test bed.

**Metric-brittleness / reward hacking.** The brittleness argument rests on a mature literature: Goodhart's law in reinforcement learning and scaling laws for reward-model over-optimisation [8], showing the proxy–true-reward gap widens predictably with optimisation pressure. The operational and prospective-data axes of the CHAP case are exactly the non-gameable tests this literature says a pure optimiser needs.

**Disease-incidence forecasting — the baselines the agent must beat.** The field is well developed, which is what makes it a fair test: hierarchical Bayesian spatio-temporal models fitted with **INLA**; **probabilistic superensembles** combining Earth-observation and seasonal-climate-forecast drivers (operational seasonal dengue forecasting in Vietnam); reproducible **ensemble ML**; and newer **spatio-temporal GNNs**, **time-series transformers**, and **time-series foundation models**. A prospective/real-time evaluation culture already exists here, which makes newly arriving partner-country data a credible, non-gameable yardstick.

## S2. Concrete methodological approaches

The agent is pointed at the field's design space and asked to develop, justify, and stress-test candidates:

- **Model families:** INLA/Bayesian hierarchical spatio-temporal baselines; gradient-boosted trees with engineered climate-lag features; spatio-temporal GNNs across administrative units; probabilistic superensembles blending mechanistic climate-driven priors with data-driven residual learners; and a fine-tuned time-series foundation model, tested for whether cross-domain pre-training helps at surveillance time scales.
- **Scoring that resists gaming:** proper scores (CRPS/weighted interval score) *plus* decision-relevant metrics — outbreak-threshold hit/false-alarm rates at usable lead times, upper-tail calibration, spatial-resolution adequacy.
- **Veridical stress tests:** denominator and reporting-delay perturbations; spatial/temporal block hold-outs; deliberate distribution-shift splits (train on one climate regime, test on another); and the prospective test on data that did not exist at development time.
- **Hybrid, knowledge-informed options:** climate-mechanistic priors (temperature-suitability curves for vector transmission) as informative priors or as a mechanistic backbone whose residuals the ML model learns.

The scientific contribution is thus a specific, benchmarked, CHAP-integrated forecasting method whose robustness is documented.

## S3. The provenance-and-agency schema

A machine-readable per-decision log with at least: **what was decided** (data-cleaning step, feature, model family, hyperparameter, acceptance of a result); **agency** — a graded field (*human-set*, *AI-on-human-assessment*, *AI-autonomous*; and for information gathering, *AI-retrieved* vs *human-pointed*); **justification** (elicited from the agent when absent); **alternatives considered and rejected**, with the basis for the trade-off (the "negative space" that makes the record veridical rather than merely reproducible); **stability annotation** (which judgment calls were perturbed and how the conclusion moved); and **immutability/accountability flags** (which entries must be tamper-evident for assurance). The deliverable wraps a re-runnable analysis in this record.

## S4. Veridical-robustness protocol

Following PCS, robustness is the object of study, not an afterthought. Each judgment call the agent makes is logged, enumerable, and automatically perturbable across a pre-registered set of reasonable alternatives; we then report the **stability of conclusions** across that set — not a single best model but the distribution of outcomes over reasonable choices, and which choices the conclusions are (in)sensitive to. This is where the agentic setting is an *advantage* for VDS: an instrumented agent can traverse the judgment-call space more completely and neutrally than a human analyst.

## S5. References

Main-text anchors [1]–[8]:

1. Gottweis, J. et al. Accelerating scientific discovery with Co-Scientist. *Nature* (2026). doi:10.1038/s41586-026-10644-y
2. Ghareeb, A. E. et al. A multi-agent system for automating scientific discovery. *Nature* (2026). doi:10.1038/s41586-026-10652-y
3. Aygün, E. et al. An AI system to help scientists write expert-level empirical software. *Nature* (2026). doi:10.1038/s41586-026-10658-6
4. Gaddipati, S. K. et al. MLReplicate: benchmarking autonomous research systems for machine-learning reproducibility. *arXiv* 2605.16616 (2026). doi:10.48550/arXiv.2605.16616
5. Starace, G. et al. PaperBench: evaluating AI's ability to replicate AI research. *arXiv* 2504.01848 (2025). doi:10.48550/arXiv.2504.01848
6. Yu, B. & Kumbier, K. Veridical data science. *PNAS* 117, 3920–3929 (2020). doi:10.1073/pnas.1901326117
7. Rewolinski, Z. T. & Yu, B. Predictability–Computability–Stability workflow for veridical data science in the age of artificial intelligence. *Phil. Trans. R. Soc. A* 384, 20240605 (2026). doi:10.1098/rsta.2024.0605
8. Gao, L., Schulman, J. & Hilton, J. Scaling laws for reward model overoptimization. *arXiv* 2210.10760 (2022). doi:10.48550/arXiv.2210.10760

Further domain references (not cited in the two-page main text): representative INLA / spatio-temporal Bayesian and ensemble-ML disease-forecasting studies (dengue, malaria); operational seasonal dengue superensemble forecasting, Vietnam.

---

#trust-project #chap #climate-health #veridical-ai #agentic-ai #supplementary
