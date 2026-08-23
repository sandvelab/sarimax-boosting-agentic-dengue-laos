# Ten simple rules for reproducible computational research in the age of agentic AI
(IS_SHADOW)

Imported source document: iteration 3 of the manuscript draft. Provenance is recorded in `provenance.md` beside this file.

---

## Introduction

Reproducibility remains the attainable minimum standard by which a computational claim can be assessed: if the path from raw data to reported result cannot be retraced, nobody — the author included — can say what the result rests on. In 2013 we proposed ten simple rules for achieving it [1]. They were written for a researcher who runs scripts by hand, takes notes by hand, and forgets by hand, and each carried a deliberately modest minimum, because the binding constraint was never knowing what to do but finding the time to do it.

That constraint has changed. **Computational research is now increasingly carried out** by agentic AI systems that plan, write and execute code in a shell, inspect the output, and iterate [2–4]. We write *your agent* for your agentic AI system, and assume the common setup: a repository you own, standing instructions in an `agent.md`-style file, an agent running on the command line.

We argue this shifts reproducibility on three fronts. It changes what is *hard*: the meticulous recording humans skipped is now nearly free, while new failure modes appear where none existed. It changes what is *pressing*: an agent can run hundreds of analyses in a day, and researcher degrees of freedom scale with it. And it changes what is *possible* — verifying that an analysis rebuilds from a clean environment, perturbing every analytic choice, testing whether your own documentation is intelligible to an outsider are all now cheap enough to do routinely. **There is also direct evidence that this needs attention: when autonomous research systems are asked to reproduce published work, they succeed considerably less often than their own fluent reports of the attempt suggest** [8,9].

**We have deliberately kept the same ten rules, and mostly the same rule names, so that what is new stands out clearly against what is not. Two things are added that did not exist in 2013. The first is veridical data science, which asks not only whether an analysis can be re-run but whether its conclusion survives being conducted differently and equally reasonably** [5,6]. **The second is a proposed setup — one complete, concrete way of organising an agentic research project that a reader can adopt directly — which covers all ten rules and the veridical requirements together. Around these we treat how to check that the rules were in fact followed, the trade-offs the agentic setting introduces, and the case for a shared community collection of reproducibility skills.**

One caveat runs through all of it. You can always ask an agent to do something, and you are not guaranteed that it will happen: a standing rule can be silently dropped late in a long session, and models are known to attend unevenly to material in a long context [11]. Agents are more meticulous than humans but **not exempt from the forgetfulness these rules were written against**, so instructions **on what to do** are not **alone** a **complete** strategy — they must be paired with checks **that give a second, independent opportunity to catch what was missed.**

## Veridical data science: reproducibility's natural extension

Reproducibility tells you what was done. **It does not tell you whether the conclusion would survive an analysis conducted differently but equally reasonably.** Veridical data science, concretely the Predictability–Computability–Stability framework [5,6], makes that second question explicit: predictability as the reality check on genuinely held-out data; computability as the reproducible-compute life cycle, essentially the ten rules; and stability as the requirement that conclusions survive the judgment calls made along the way — cleaning, filtering thresholds, metric choice, model family.

These values were already in the reproducibility movement; PCS **, which has arrived more recently,** names them and makes them checkable. We fold them in because **a** dominant source of wrong conclusions **is** instability under **alternative** reasonable **choices**, and against that, reproducibility is necessary **to document the choices** but not sufficient **to show their implications**. Sharing code lets a reader re-run your choices; it does not tell them whether those choices mattered.

Agentic AI sharpens both sides. It is a threat: an agent makes judgment calls silently and fast, so an analysis can be **inappropriately** tuned to available data **or metrics** far quicker than a human could manage — the classic over-optimisation failure [7], with the optimiser now inside the loop. It is also **a potential** remedy: an instrumented agent can enumerate the calls it made, perturb each across a pre-specified set of **reasonable** alternatives, and report the distribution of conclusions rather than the best one. Which of the two you get is a design choice, not a property of the technology.

This adds one requirement to every rule below: record not only what was done, but the alternatives considered and rejected, on what basis, and whether the conclusion moves when they are taken instead.

## Rule 1: For every result, make your agent keep track of how it was produced

***Every result that may be of interest should be traceable to the specific sequence of steps that produced it — that particular figure, table or number tied to the particular commands, scripts, parameters and inputs behind it*** [1].

**What this rule asks for in the agentic setting is a pairing: each identifiable result — a figure, a table, a number, a statement — held together with the detailed execution history that produced it.** The agent knows the exact command it issued; it need not reconstruct it a month later. What it needs is a standing instruction binding **every** identifiable result to the script and invocation that produced it, so **the link is written down as the result is produced rather than reconstructed afterwards.**

**Three failure modes are new enough to guard against explicitly.**

**First, steps that leave nothing on disk. The agent runs a script, reads a number off its printed output, and uses that number in the next step — as a threshold, a normalisation constant, an argument to a second script — without ever writing it to a file. Nothing in the repository records that the step happened. The remedy is a checkable invariant: no value passes from one step to the next except through a file.**

**Second, commands that exist only in the session. An agent will readily type a one-off command in the shell instead of saving it as a script. The command is in the transcript, and the transcript is not part of the repository. The remedy is the same one the original rule gave, now easier to meet: everything that runs is a file that was executed.**

**Third, an account that reads as complete when it is not. The agent's summary of what it did is fluent and plausible whether or not the record behind it is intact, so gaps are hard to notice by reading. This is what makes the invariant checks of a later section worth building — reading the narrative is not a way to verify the record.**

## Rule 2: Avoid manual data manipulation steps — or make them tracked inputs

*Rely on programs rather than manual edits: hand modification is inefficient, error-prone, and by its nature leaves no trace that can be re-enacted [1].*

The temptation does not disappear; it relocates. **It may be less tempting to** hand-edit a data file, but you will be tempted to hand-edit the agent's artifacts — a parameter, a path, an intermediate table, a plan — because natural language is ambiguous and correcting the output is often far faster than re-specifying the input. This happens more than one expects, and it is exactly as corrosive as before: the pipeline no longer runs end to end.

Two strategies work. Refuse manual edits and iterate on the **instruction to the agent, accepting the delay and the several rounds of clarification this may take**. Or — and here the agentic setting is genuinely better than classical analysis — make manual editing a first-class, tracked step. **The convention is that the agent's own file is never touched: the agent writes `result.csv`, and a human edit goes into a separate copy, `result_edited.csv`.** The agent recognises the pair, treats the edited file as authoritative downstream, and generates a diff that enters the provenance record as a **step of human input**. These artifacts are small, so keeping both costs nothing, and manual intervention becomes visible, summarised and re-enactable — better tracked than the manual steps the original rule could only ask you to avoid.

**The stored diff also solves the problem that otherwise makes this convention wear out. When the agent later regenerates its own file, the human edit made against the previous version would ordinarily be lost. Instead, the agent can take the diff for the old pair and apply the corresponding change to the new file, producing an updated edited version — reliably where the regenerated file changed only slightly, and with the diff to fall back on for review where it did not.**

## Rule 3: Archive the exact versions of all external programs used

*Exact reproduction may require the exact versions **of programs** originally used, and obtaining an old version later is often far from trivial [1].*

Agents are good at this for the same reason they are good at Rule 1: it is detailed, tedious work with well-established solutions. Ask for a pinned specification — lockfile, container image — and you get one with its build recipe. More importantly, ask for it to be *verified*: an agent can build from scratch in a clean directory and re-run the analysis end to end, the check that was always recommended and almost never performed.

The rule also gains a longer horizon. Much of what made old software unusable was not the missing version but the cost of making it build again — patching source against a current toolchain, replacing a vanished dependency. **That work is now often tractable rather than a reason to give up**, so analyses depending on exact or ancient tools stand to stay reproducible considerably longer.

## Rule 4: Version control all custom scripts

*The smallest change to a script can change its output, so only the exact code state that produced a result can reproduce it [1].*

**The principle is unchanged; the rate of change is not. An agent may rewrite a script several times within a single response, so the code state behind any given result exists only briefly. Committing once at the end of a session is then too coarse a granularity to be useful: by the time the commit is made, several versions have come and gone, and there is no way to say which of them produced which result. The fix is to tie commits to results — commit before and after each analysis run, and write the commit hash into that result's provenance record from Rule 1. Small frequent commits cost nothing, and the history is not being written to be read as a narrative; it is an addressing scheme for results.**

**The instruction files — `agent.md`, the skills, the conventions — should be version-controlled too, but for a different reason, and it is worth being clear about which. They are not part of the reproduction path: once the agent has settled on a particular set of scripts, those scripts and their environment are what produce the reported result, and re-running them does not consult the instructions at all. What the instructions did was shape which analysis the project arrived at. That makes them part of the veridical record rather than the reproducibility record — evidence about how the analysis came to look the way it does, alongside the alternatives that were considered. Version-control them, archive them, and note in the provenance record which version was in force when a result was produced.**

## Rule 5: Record all intermediate results, when possible in standardized formats

***Intermediate results can in principle be regenerated from the raw data, but storing them reveals discrepancies invisible in the final output, shows the consequences of alternative choices, lets single steps be rerun, and localises where reproduction breaks*** [1].

**Every one of those benefits still holds. What has changed is the cost, which is why the original had to hedge with *when possible*. That cost was human: writing serialisation code at each step, choosing a format for each data type, judging where storage becomes prohibitive, and later writing further code to summarise the intermediates or to re-enter the pipeline partway. An agent does all of this on request. One standing instruction covers the writing — store intermediates at every step, in a suitable standard format, unless space is prohibitive — and the code needed to inspect them or to run a sub-pipeline from one of them is written when it is wanted and discarded afterwards.**

**The benefit side has grown as well. Stability checks are run mostly at intermediate stages, because that is where the judgment calls sit: a filtering threshold, a normalisation, a choice of feature definition. Varying such a choice requires the output of the preceding step to exist on disk, in a form that can be modified and fed downstream again. Cheap, well-formatted intermediates are therefore what makes the checks of the later sections affordable at all.**

## Rule 6: For analyses that include randomness, note underlying random seeds

*Given the same seed a stochastic analysis yields identical results; recording seeds is what distinguishes exact **from** approximate reproduction [1].*

**The obstacle was never understanding the rule but achieving full coverage. Every component has to be seeded, including the awkward cases: parallel workers, subprocesses that reseed from system entropy, library-level global state, hash randomisation, and nondeterministic hardware kernels. Exhaustive coverage of a checklist like this is what agents do well. They can also close the loop rather than merely record: seed everything, run the analysis twice, diff the outputs, and treat any difference as a defect in the seeding to be located.**

One wrinkle deserves stating plainly, because two things are easily conflated. **The agent itself is stochastic, and its output is not reproducible from a seed.** Ask the same question twice and you get two different scripts. This is not a defect to engineer away; it is a statement about what reproducibility means here. What must be reproducible is the *artifact* — script, environment, seeds, results — not the process that generated it. The record of that process belongs to provenance and to Rule 9, and is valuable for a different reason: it lets a reader see what was tried and why, not re-derive it.

## Rule 7: Always store raw data behind plots

*A figure is remade many times before publication; keeping the numbers behind it means changing the plot without redoing the analysis, and lets exact values be read off [1].*

**One could argue this matters less now, since an agent writes plotting code in seconds and can often recover values from a rendered figure to near-pixel accuracy. The opposite conclusion is the right one. The number of figure iterations goes up sharply when a variant is one sentence away, and every round that regenerates the analysis to redraw the figure costs tokens, wall-clock time, and an opportunity for the numbers to drift. Storing the plotted values is exact, costs almost nothing in space, and removes all three.**

**Implementing this requires one standing instruction to the agent: whenever a plot is produced, the plotted values and the plotting script should be written beside it.** As in the original, store both the pre-aggregation values and the values actually drawn where these differ.

## Rule 8: Generate hierarchical analysis output, allowing layers of increasing detail to be inspected

***Primary reported** results are **often** heavy summaries; validating and understanding them **often** requires the detail underneath, and linked hypertext lets a **human effectively** descend from a summarised value to the data behind it [1].*

**What has changed is that the detail now has two readers rather than one.** The first is the agent: having the detail already on disk saves tokens and recomputation, and avoids the churn of inserting temporary debug output into working code and removing it afterwards, which is a real source of silent breakage. The second is you. You can ask the agent to investigate, but a conversation is a narrow channel; a browsable structure you descend by clicking uses human scanning bandwidth that no dialogue matches. For understanding your own results — and for spotting the anomaly only domain context makes visible — the old-school linked HTML report remains superior.

What has changed is who builds it. Previously you emitted every level yourself and wired up the links. This is generic work a single reusable skill can do across projects, which is why we propose it as one of the community skills below.

## Rule 9: Connect textual statements to underlying results

*Interpretations live in text while results live in files; **it is difficult and error-prone to reconnect** a claim to the result **inspiring and** supporting it after the fact, so the connection should be made when the statement is first formulated [1].*

**Human grounding of a statement is partly intuitive: you are informed by a result, and by other results, and by the literature, and the mapping is rarely one-to-one or even recoverable to yourself afterwards. An agent can be asked to work systematically instead, and doing so serves a second purpose — requiring each generated sentence to name a stored result is among the more effective practical defences against fabricated content and against text drifting away from the analysis it describes.**

We therefore propose writing a paper in two steps. The first goes from results to a **claim collection**: short textual statements — interpretations, claims, conclusions — each carrying an explicit pointer to the results grounding it. The second assembles the manuscript from that collection, whether drafted by the agent, drafted by a human with findings inserted, or a mixture. Sentences then carry a provenance annotation, in a sidecar file, back to the claim and thence to the result and the script.

This pays off three ways. Claims become an object you can search and reason over — everything the analysis supports, independent of what reached the paper. Provenance runs unbroken from sentence to command. And it works retrospectively: for a human-written draft, the agent can match each statement against the collection and flag the ones with no support, a useful and **potentially** slightly uncomfortable exercise.

## Rule 10: Provide public access to scripts, runs, and results

*All input data, scripts, versions, parameters and intermediate results should be publicly and easily accessible; this signals quality and makes the work usable by others [1].*

If the preceding rules held, this one is nearly free: ask the agent to gather the material, structure it, and push it **into a public repository**. The process is standard and needs little human intervention.

What has grown is *what is worth publishing*. Beyond scripts, data and results, the artifacts of this setup are part of the method and belong in the release: the instruction files and skills, which shaped how the agent worked; the claim collection; and the provenance record of how the analysis came about — the explorations that failed, the alternatives rejected, the basis for each trade-off, and which decisions were the human's and which the agent's. **That record is what makes a reproducible analysis a veridical one, and it is the part a critical reader has the most use for.**

Two hazards are new enough to name. Agents will cheerfully commit credentials, and cheerfully publish data that governance does not permit. Make a secrets scan and a permission check part of the release step rather than part of your memory.

## A proposed comprehensive agentic AI setup to cover all rules

**We here describe one concrete arrangement that aims to meet all the proposed rules by construction, and to cover the veridical requirements of the earlier section along with them. It is one arrangement among several that would work. We offer it as a baseline that can be adopted as it stands, and as a starting point for a setup better fitted to your own work.**

**The organising object is a tree of claims.** **Ask your agent to organise the project as a tree in which each node is one *claim*: a question the project sets out to explore, written as a sentence or two of plain text, together with the analysis addressing it. *Claim* here means something claimed to be worth exploring, not something asserted to be true — the statements the analysis ends up supporting are what Rule 9 handles. The tree is a map of the project's questions, and the scripts hang off it.**

**A node's children are of one of two kinds**, **and the kind is a property of the node's whole set of children rather than of individual edges. Where a single question needs both kinds, insert an intermediate node.**

***Sub-analyses* are the basic case.** **The children are the supporting parts of the parent's analysis: each child claim covers a sub-part of a parallel or sequential approach to the parent claim. The parent's main script calls every child's main script, in the order the approach requires, together with the parent's own scripts — typically the ones that combine what the children produced. Nesting sub-analyses decomposes the project's overall question into steadily finer-grained sub-questions. That decomposition is itself useful: it is what lets any particular piece of execution be tied to the aspect of the overall claim it serves.**

***Alternatives* are what the veridical requirements need.** **The children are competing paths explored for the same parent claim: each child claim is one possible interpretation of the parent claim, or one possible strategy for answering it. One child is annotated as the main analysis path, and the parent's main script then calls only that child's main script — an alternatives node holds no scripts of its own and acts as a switch. The paths not taken stay in the tree, with their claims and scripts intact and independently runnable, but off the route that reproduces the reported analysis. This is where the judgment calls that stability analysis is concerned with get written down in executable form rather than described in prose, which is what an ordinary repository has nowhere to put.**

**Each node holds four things.** **The claim, as text. A main script that runs everything belonging to the node — in practice a short list of shell lines, containing calls to the main scripts of the node's children and calls to the scripts stored at this node. The scripts themselves, as a folder, or as a zip file at archival. And whatever the node needs to set up its computational environment beyond that of the full analysis, which for most nodes is nothing.**

**The root reproduces the main analysis result.** **Because each node's main script calls its children's, running the root node's main script runs the whole analysis, taking the main path at every alternatives fork, and ending at the reported result. That this holds is checkable rather than assumed: build the environment on a clean machine, run the root script, and compare against the archived results.**

**What a stability analysis additionally requires of the root.** **Reproducing the main path is not enough for the stability pillar of PCS; the root must also be able to walk the alternatives. Three things make that possible. Alternative siblings must share an output contract, so that any of them can be substituted at that fork and the downstream nodes still run. The reported conclusion must be computed by a script rather than asserted in the text, so that it can be recomputed once for each combination of alternatives. And the set of forks to vary must be enumerated in advance, with a computational budget attached, since the number of combinations grows multiplicatively. Given these, a run of the root in stability mode returns a distribution of conclusions over reasonable analyses instead of a single one, and what was left unexplored for budget reasons is on record rather than absent.**

**One environment, with local overrides.** The full analysis has a single main environment, used generally. A node may extend or override it where it genuinely needs something else, and that specification lives with the node. **Keeping overrides rare keeps the number of environments a reproducer has to build small, and makes every exception visible.**

**How the tree carries the other rules.** **A node's path is a stable address, which is what the provenance records of Rule 1 point at, what the claims of Rule 9 attach to, and what the release of Rule 10 is organised around. The hierarchical output of Rule 8 relates to the tree but is not the same thing, and the two are worth keeping apart: the tree is a hierarchy over the project's questions, while Rule 8 also asks for hierarchy *within* a result — a national average with the per-region values behind it, for instance, which belongs inside one node's results and has nothing to do with the claim structure. A good report uses the tree for its upper levels and the within-result hierarchy below that.**

## Validating that the rules were actually followed

**An instruction is not a guarantee: a standing rule can be honoured for twenty steps and quietly dropped at the twenty-first, with nothing in the output looking wrong.**

The remedy is to stop relying on the agent remembering. Two kinds of check are worth building.

**Deterministic invariant checks.** A script, run at the end of every analysis and on every commit, verifying the properties the rules imply: every result file has a provenance record; every plot has its data and script beside it; every claim resolves to an existing result; the working tree is clean and the recorded hash matches; every stochastic step has a seed. These are ordinary code, and unlike instructions they have no attention budget. **Running them continuously rather than at the end means problems surface while both the agent's context and your own recollection of the step are still fresh.**

**The outsider test.** **Reproducibility documentation is written by the person for whom everything is already obvious, and whether it is intelligible to anyone else used to require recruiting someone else to find out. It can now be tested directly: start a fresh agent with no prior context, give it the repository and its instructions, and ask it to reproduce the analysis. What it misunderstands is what an outsider would misunderstand. The test is cheap enough to repeat whenever the documentation changes, and replaces a judgment that was never reliable with an objective check.**

Neither removes the underlying uncertainty, and we expect the problem to recede as these systems improve. The honest position for now is that a well-instructed setup makes reproducibility likely rather than certain, and that the gap should be closed by verification rather than assumed away.

## Trade-offs

The original rules were built around one trade-off: reproducibility against the researcher's time. That has largely dissolved, and three others take its place.

**Agent processing against human effort.** Nearly everything above converts human effort into tokens and wall-clock time. This is usually an excellent exchange and is why the minimum levels of the original rules can be raised. But it has a characteristic failure: because each request is individually cheap, thoroughness expands without anyone deciding that it should. State the level of tracking a project warrants and instruct to it — exploratory work that will mostly be thrown away has always deserved a lighter touch than work whose conclusions will be defended [10].

**Reproducibility against storage.** More stored intermediates, versions and environments make reproduction easier; occasionally the volume becomes prohibitive. The useful new option is to defer the decision: have the agent annotate what it stores with a small record — main or side result, regenerable or not, at roughly what cost, how important for transparency — and prune later **if needed** against those annotations. Rough estimates suffice. Deleting up front, the old option, destroys precisely what cannot be recovered.

**Robustness against computation.** **The stability analysis of VDS** means running **the full data science life cycle for** an analysis many times over reasonable variations. Agentic AI makes *specifying* those variations nearly free, which exposes the computational budget as the binding constraint. Have the agent estimate the cost of each perturbation and prune consistently against a stated budget, so that what was and was not explored is a recorded decision.

## Generically useful agentic skills for reproducibility

Almost everything **described in this paper** is generic. Exhaustive seeding, hierarchical report generation, maintaining a claim collection, checking invariants, clean-room verification — none is specific to a project, a field or a dataset. They should be written once, well, and reused rather than re-derived in every repository.

We therefore propose a community collection of reproducibility skills for agentic research: instruction modules, each with its motivation and intended behaviour, published as an open repository that the community extends by pull request. The initial set follows this paper — roughly one skill per rule, plus supporting ones for the claim collection, clean-room verification and invariant checks. The organisational model we have in mind is the one that has worked for community-curated bioinformatics workflows, **nf-core being a good example** [12]: a shared structure, review by others before inclusion, versioning, and an explicit purpose statement per contribution. Security screening is a requirement rather than a footnote, since an instruction module is executable influence over someone else's agent.

One further skill is the natural closing step of a project. After an analysis is finished, have the agent produce a **reproducibility report**: starting from the final text — which need not be a manuscript — it walks back through the claims, results, scripts, environments and provenance, and states what exists and how it can be tracked **and re-run**. A provenance graph over the claim tree is a good backbone, and the veridical material belongs in the same document.

## An illustrating case

**To be written later.**

## Conclusion

The ten rules **to ensure reproducibility** have not changed **their character much,** and we **also** do not expect them to **in going ahead**. What has changed is that the reason they were so often ignored — that following them properly **was costing** more care and time than **many** working **researchers felt they** could spare — no longer applies with much force. The tedious parts are cheap **and** several previously theoretical checks are routine. **Researchers should exploit this opportunity to raise the level of reproducibility of their analyses. And correspondingly, the** minimum acceptable standard should rise accordingly.

A subtler constraint replaces the old one. An agent will follow your instructions most of the time, generate far more analyses than you can inspect, and produce a fluent account of all of it. Reproducibility here is less about discipline than about design: build the recording into the structure, verify rather than trust, and keep the record of what was *not* done alongside the record of what was.

## Declaration of human use

**I wrote this text. I am an agentic AI system and drafted this manuscript in full as its sole writer, from the idea and the specific written directions provided by Geir Kjetil Sandve. This particular version is iteration 3, produced on 22 August 2026, and was written solely by me; later versions may have been changed further by human hands. The process is ongoing: at each round the human director gives concrete input on how the content should change — in this round as tracked edits and comments on the previous version — and I revise accordingly. The conception is his: the aim of updating his 2013 rules for the agentic setting, the position taken on each rule, the proposed project setup, the veridical framing, and the scope of the paper. He has read the full text critically and, by submission, will have taken complete responsibility for all of it. In standard contribution terms: **conceptualization, methodology, supervision** — Geir Kjetil Sandve; **writing (original draft)** — the AI system; **direction, critical review, final responsibility** — Geir Kjetil Sandve.**

---

## References

1. Sandve GK, Nekrutenko A, Taylor J, Hovig E. Ten simple rules for reproducible computational research. *PLoS Comput Biol* 9(10): e1003285 (2013). doi:10.1371/journal.pcbi.1003285
2. Gottweis J, et al. Accelerating scientific discovery with Co-Scientist. *Nature* (2026). doi:10.1038/s41586-026-10644-y
3. Ghareeb AE, et al. A multi-agent system for automating scientific discovery. *Nature* (2026). doi:10.1038/s41586-026-10652-y
4. Aygün E, et al. An AI system to help scientists write expert-level empirical software. *Nature* (2026). doi:10.1038/s41586-026-10658-6
5. Yu B, Kumbier K. Veridical data science. *PNAS* 117: 3920–3929 (2020). doi:10.1073/pnas.1901326117
6. Rewolinski ZT, Yu B. Predictability–Computability–Stability workflow for veridical data science in the age of artificial intelligence. *Phil Trans R Soc A* 384: 20240605 (2026). doi:10.1098/rsta.2024.0605
7. Gao L, Schulman J, Hilton J. Scaling laws for reward model overoptimization. *arXiv* 2210.10760 (2022). doi:10.48550/arXiv.2210.10760
8. Gaddipati SK, et al. MLReplicate: benchmarking autonomous research systems for machine-learning reproducibility. *arXiv* 2605.16616 (2026). doi:10.48550/arXiv.2605.16616
9. Starace G, et al. PaperBench: evaluating AI's ability to replicate AI research. *arXiv* 2504.01848 (2025). doi:10.48550/arXiv.2504.01848
10. Balaban G, Grytten I, Rand KD, Scheffer L, Sandve GK. Ten simple rules for quick and dirty scientific programming. *PLoS Comput Biol* 17(3): e1008549 (2021). doi:10.1371/journal.pcbi.1008549
11. **Liu NF, Lin K, Hewitt J, Paranjape A, Bevilacqua M, Petroni F, Liang P. Lost in the middle: how language models use long contexts. *Trans Assoc Comput Linguist* 12: 157–173 (2024). doi:10.1162/tacl_a_00638**
12. **Ewels PA, Peltzer A, Fillinger S, Patel H, Alneberg J, Wilm A, et al. The nf-core framework for community-curated bioinformatics pipelines. *Nat Biotechnol* 38: 276–278 (2020). doi:10.1038/s41587-020-0439-x**

---

## Appendix — working material, not part of the manuscript

Section by section under the same headings, the detail that did not fit the main text.

### Introduction

**On the premises.** The rules assume an agent operating on a repository you own, with standing instructions in a file it reads at the start of every session, executing shell commands as part of its response. Other arrangements — a hosted notebook agent, an IDE-embedded assistant, a managed research platform — change the mechanics of several rules but not their substance. Where a platform already handles a rule, as integrated workflow frameworks did in 2013 [1], your task is to know how to exploit that rather than to reimplement it.

**On what "reproducible" means when a model is in the loop.** Three things are easily conflated and worth separating. *Artifact reproducibility*: given the released repository, does re-running produce the same results? This is what the ten rules deliver, and it is fully achievable. *Process reproducibility*: would asking the agent the same question again produce the same analysis? It would not, and no seeding fixes this. *Conclusion stability*: would a reasonable alternative analysis support the same conclusion? This is the veridical question, and the one that most determines whether the science is right. The rules target the first, supply the raw material for the third, and deliberately give up on the second.

**On the forgetfulness point.** That a standing instruction can be silently ignored is not a criticism of any particular system, and the degree varies with context length, instruction placement, and how much else the agent is holding. **The clearest documented form of this is positional: models attend unevenly across a long context, with material placed in the middle of it used considerably less reliably than material at either end [11]. Instruction-dropping in a long agentic session is the practical face of the same phenomenon, and is not as precisely characterised in the literature as the retrieval case — which is itself a reason to verify rather than to rely on an estimate of how often it happens.** The implications are consistent across systems: keep the standing instruction set small enough to be attended to, restate critical invariants close to where they apply, and verify with code rather than with reminders.

**Why the rules needed revisiting at all.** The 2013 minimums were pitched at what a busy researcher would actually do, not at what was ideal. Nearly all of those minimums are now dominated: there is no longer a good reason to settle for "note the exact names and versions of the main programs" when a verified lockfile costs one instruction. Raising the minimums is the single largest practical consequence of the shift, and it applies to every rule below.

### Veridical data science: reproducibility's natural extension

**The three pillars, concretely.** *Predictability* asks whether the result holds against reality — genuinely held-out data, ideally data that did not exist when the analysis was designed and therefore cannot have influenced it. *Computability* covers the reproducible-compute life cycle and maps almost exactly onto the ten rules. *Stability* generalises uncertainty quantification from sampling variability to the whole space of judgment calls: cleaning and filtering, feature definitions, algorithm and hyperparameter selection, and the choice of evaluation metric.

**Why instability rather than sampling noise is the target.** In settings with strong dependence structure, standard false-discovery control can still admit large numbers of false positives; the more simplistic the assumed null model, the higher the false-finding rate; and the choice of summary metric alone can reverse a conclusion while every alternative looks entirely plausible to domain experts. These are the reasons for insisting that computational reproducibility is necessary but not sufficient. A perfectly reproducible pipeline reproduces a fragile conclusion perfectly.

**A further criterion in applied settings.** Where the work has a real deployment context — a clinical decision, an operational forecast — whether the result holds up in that use is itself evidence about its veridicality, and arguably the strongest kind. This does not generalise to every analysis and should not be forced onto exploratory work, but where it applies it is worth working backwards from the decision to the model and only then to the data.

**Why agentic AI raises the stakes.** Researcher degrees of freedom were always limited in practice by how many analyses a person could run. That limit is gone. An agent can traverse a large analytic space quickly while optimising against whatever target it was given, which is the setting in which proxy targets and true objectives diverge most reliably [7]. Left unattended, this is a plausible route to a considerably larger replicability problem than the one we have. The same capacity, instrumented and pointed at the perturbation space instead of at the metric, is the best tool we have had for stability analysis.

**Where the agent's own variability becomes a stability probe.** Two independent sessions given the same analytical brief will make different but often equally defensible choices. Running a brief through several independent sessions and comparing the conclusions is therefore a perturbation of exactly the judgment-call space veridical analysis is concerned with — an unusual case where the technology's least reproducible property is directly useful.

### Rule 1: For every result, make your agent keep track of how it was produced

**What a provenance record should contain.** At minimum, per identifiable result: the script file and its commit hash; the exact invocation with all parameters; the input files with content hashes; the environment identifier; the random seeds; the timestamp; and a pointer to the node in the claim tree it belongs to. For the veridical extension, add the alternatives considered at this step, the stated basis for the choice, and whether the step was decided by the human or the agent.

**Grading agency.** A field with no analogue in a human-only workflow records who actually decided: *human-set*, *agent-on-human-assessment*, *agent-autonomous*; and for information gathering, *agent-retrieved* versus *human-pointed*. Where an agent makes most of the analytic judgment calls, this is the field that lets a reader understand what the human contribution actually was, and it is likely to become a normal expectation of published work.

**The three new failure modes, in detail.** *Values that never reach disk.* The characteristic form is subtle: the agent runs a script, reads a number from its printed output, and uses that number in the next step — as a threshold, a normalisation constant, an input to a second script — without ever writing it down. The invariant that catches it is that no value crosses between steps except through a file, and it is mechanically checkable if steps are required to declare their inputs. *Commands that live only in the transcript.* An agent asked to "just check something quickly" will type a command rather than write a script; the result may then be used, and the command is nowhere in the repository. Requiring every executed command to originate in a tracked file makes this a check rather than a habit. *Narrative that outruns the record.* The agent's own account of a session is fluent whether or not the underlying record is complete, which means reading the session is not a way to verify it. **This is the specific reason the invariant checks are worth building even for a careful operator: they inspect the repository, not the story about the repository.**

**Binding results to the claim tree.** A provenance record that points only at a script answers "how was this made" but not "what was this for". Recording the claim-tree node as well is what makes the record navigable in both directions, and is what the hierarchical report of Rule 8 and the claim collection of Rule 9 are both built on.

### Rule 2: Avoid manual data manipulation steps — or make them tracked inputs

**Why the temptation is stronger than it looks.** The gap between what you meant and what you got is the fundamental friction of natural-language instruction, and it does not close asymptotically — you can spend three rounds failing to convey a change that would take four seconds by hand. The rational response is not to pretend the temptation away but to make giving in to it harmless.

**The edited-copy convention, in practice.** Adopt a fixed suffix (`_edited`) and a standing rule with four parts: the agent never edits or overwrites its own output; a human edit is made in a separate copy carrying the suffix; when a file exists both with and without the suffix, the suffixed one is authoritative downstream; and the agent generates and stores a diff whenever it detects such a pair, summarising it into the provenance record as an input step with the human named as its author. Manual intervention then appears as a first-class, inspectable node rather than an unrecorded discontinuity.

**Carrying a human edit forward across regeneration.** **The convention as stated has a weakness: as soon as the agent regenerates its own file, the edited copy is an edit of a version that no longer exists. The stored diff is what resolves this. Given the diff between the old pair, the agent can apply the corresponding change to the newly generated file and produce an updated edited copy, which is reliable where the regenerated file differs only slightly from its predecessor and needs review where it does not. The re-application is itself an agent action and is recorded as one, so the provenance now carries both the original human edit and each subsequent carry-forward. Where the regeneration changed the file substantially, the honest outcome is to flag the conflict and have the human redo the edit rather than to guess.**

**Prompts and sessions are inputs.** Where the agent writes the code, the instruction that produced the code is at least as informative as the code. Retain `agent.md` and the skills under version control (Rule 4), and retain session transcripts as archived material. They are small, and they are the only record of the reasoning that shaped the analysis.

**A caution on the convention.** It works because the artifacts are small and text-like. Applied to a large binary intermediate it degrades into storing two copies and a useless diff; there, prefer re-specification, or record the edit as a scripted transformation instead.

### Rule 3: Archive the exact versions of all external programs used

**Layered environment specification.** Three levels are worth distinguishing: a declarative specification (the environment file you wrote), a resolved lockfile (exactly what was installed, with versions and hashes), and an image (the whole thing, frozen). The first is readable, the second is what actually reproduces, the third is what survives when upstream package repositories change or disappear. Store all three where the analysis matters; the first two always.

**The clean-room check.** From an empty directory and a clean environment: build from the specification, fetch the inputs, run the root script, compare outputs against the archived ones, and report differences rather than asserting success. This catches the whole class of errors where an analysis silently depends on something in your working directory or your shell environment.

**Resurrecting unmaintained tools.** Where an analysis depends on software no longer maintained, patching source to build against a current toolchain, replacing an abandoned dependency, or writing a compatibility shim are all now tractable agent tasks. Treat the patched version as a custom script: version-control it, archive it, and record the patch alongside the original.

**The limits.** None of this survives a vanished data source, a licence server, or a hardware dependency. Where such a dependency exists, say so explicitly in the release rather than leaving a reproducer to discover it.

### Rule 4: Version control all custom scripts

**Commit granularity tied to results.** Any result you might report should correspond to a commit. Instruct the agent to commit before an analysis run and after it, with the run recorded in the message, and to write the hash into the provenance record. Frequent small commits are cheap, and the history is not for human reading anyway — it is an addressing scheme.

**Where the instruction files belong, and where they do not.** **It is tempting to say that two runs of the same repository under different instructions are two different methods, but that overstates the case and mislocates the point. Once the agent has arrived at a particular set of scripts, those scripts and the environment are what produce the reported result; reproduction re-runs them and never consults `agent.md`. So the instruction files are not part of the reproduction path, and a reproducer does not need them to obtain the result.**

**What they are is part of the account of how the project arrived at the analysis it reports — the same category as the alternatives that were explored and the basis on which choices were made. That places them in the veridical record. Two consequences follow. They should be version-controlled and archived, and the provenance record should note which version was in force when a result was produced, so that a reader assessing whether the analysis was a reasonable one can see what was steering it. And a mid-project change to them is worth flagging as such, not because it breaks reproduction but because it may explain why the analysis before and after that point differs in character.**

**What not to version-control.** Large intermediates and data belong in a data store with content-addressed references from the repository, not in git history. The distinction is between things whose *evolution* matters — code, instructions, claims — and things whose *identity* matters.

### Rule 5: Record all intermediate results, when possible in standardized formats

**Format selection, delegated.** The original's *when possible in standardized formats* was a real constraint when someone had to write the serialisation code. It is now reasonable to state the preference and let the agent apply it: standard, self-describing, language-agnostic formats where they exist for the data type; a documented plain-text form where they do not; and never a language-specific pickle for anything that must outlive the session.

**What the intermediates buy that is new.** Beyond the five reasons in the original rule, two matter here. Partial re-execution is cheap to arrange on demand — an agent can build a sub-pipeline entering at any stored intermediate in minutes, which turns "we could in principle re-run from step four" into something people do. And perturbation happens at intermediates: asking how much a conclusion moves when an upstream threshold changes requires the upstream output to exist in a form that can be varied and re-fed downstream.

**When to say no.** The reasonable-judgment exception is still real. Per-iteration outputs of a long sampling procedure, full intermediate tensors in a deep model, or anything on the order of raw data times the number of steps will not be stored. Store a summary at those steps instead, annotate what was skipped and why, and record the cost of regenerating it — which returns to the storage trade-off.

### Rule 6: For analyses that include randomness, note underlying random seeds

**The coverage checklist.** Sources that get missed: the language-level global generator; each library's own generator; per-worker seeds under multiprocessing and the seeding of workers spawned by a data loader; subprocess invocations that reseed from system entropy; hash randomisation affecting iteration order over sets and dictionaries; nondeterministic reduction order on GPUs; and nondeterminism in the environment itself, such as thread counts affecting floating-point summation order. A single project-level seed, deterministically derived into per-component seeds and recorded, is more robust than seeding each site independently.

**Verify by re-running.** Seeding is only credible when checked. Run twice, compare outputs bit for bit, and treat any difference as a defect to be located rather than tolerated. Where exact equality is genuinely unattainable — some GPU kernels, some parallel reductions — record that fact along with the achievable tolerance, so a later reproducer knows what to expect.

**The agent's own nondeterminism, restated.** Two independent sessions will produce different code, different variable names, sometimes different but equally defensible analytic choices. Do not attempt to suppress this by fixing a sampling temperature; it does not achieve what it appears to, and it is not what reproducibility requires. What it does mean is that the *transcript* is not a specification — the archived artifacts are.

### Rule 7: Always store raw data behind plots

**What to store beside each figure.** The values actually plotted, in a tabular text format; the pre-aggregation values where the plot summarises (the observations behind a histogram, not only the bin heights); the plotting script; and the provenance entry linking these to the result they visualise. A handful of kilobytes in the typical case.

**On extracting values from figure images.** An agent can often recover plotted values from a rendered figure to good accuracy, which is genuinely useful when working with someone else's published figure. It is not a substitute for storing your own numbers: the recovery is approximate, it silently fails on overlapping or clipped elements, and it cannot recover what the figure aggregated away.

**Why the iteration count matters more than it used to.** The practical case for this rule was always that figures get remade. When remaking one is a sentence away, several rounds of variants per figure become normal, and the cost of regenerating the analysis each time is paid repeatedly rather than once.

### Rule 8: Generate hierarchical analysis output, allowing layers of increasing detail to be inspected

**Two hierarchies, and why they are not the same.** **The claim tree of the setup section is a hierarchy over the project's questions. The hierarchy this rule asks for is a hierarchy over levels of detail within results, and the two do not coincide: a reported national average and the per-region values behind it are two levels of one result produced at a single node, with no corresponding parent and child in the claim tree. A generic report generator should therefore take both — the tree for the upper structure, so the report follows the analysis rather than being maintained separately, and each node's own result hierarchy below that. Requiring the report's structure to be exactly the claim tree would push detail levels into the tree that do not belong there.**

**Structure of a generic hierarchical report.** Each summarised value in the top-level report links to the values it aggregates; each of those to its own inputs, down to the raw level. Each node carries its provenance record and environment. Static HTML is the right technology precisely because it will still open in twenty years.

**Why this beats asking the agent.** Cost: retrieving stored detail is free where regenerating it is not. Fidelity: the stored values are what the analysis actually produced, not what a later reconstruction produces. Bandwidth: scanning a structure visually for the thing that looks wrong is something humans do far faster than they can describe what they are looking for, which a dialogue would require.

**The debug-output anti-pattern.** The common alternative — having the agent add print statements, run, read, and remove them — is worse than it looks. It modifies working code, sometimes leaves residue, occasionally changes behaviour, and produces output that is discarded rather than archived. Permanent structured output at the point of generation avoids all four.

### Rule 9: Connect textual statements to underlying results

**Anatomy of a claim.** A claim entry holds: the statement in one or two sentences; pointers to the results grounding it, at the granularity of a specific stored file or value; the claim-tree node it belongs to; a confidence or scope qualifier; the alternatives that would have supported a different statement and why they were not taken; and whether the statement was authored by the human or the agent. The collection is a file or small database in the repository, versioned with everything else.

**The two-step writing process.** Step one is generation: from results to claims, done systematically and checked. Step two is composition, in any of three modes — the agent drafts from the collection; the human drafts and the agent inserts grounded findings; or the human drafts freely and the agent afterwards matches each sentence to the collection. The third is the retrospective audit, worth running even on a fully human-written manuscript: statements with no match are either unsupported or point to a claim you forgot to record, and both are worth knowing.

**Provenance annotation in the manuscript.** Keep the annotation out of the reader's way but in the source: a sidecar file keyed by paragraph or sentence identifier is more robust than inline comments, survives format conversion, and can be published as supporting material. The end state is a document in which any sentence traces to a claim, a result, a script, a commit and an environment.

**Why this is also the hallucination control.** Requiring each generated sentence to name the stored result it rests on constrains generation to what exists. It does not eliminate fabrication — a pointer can be attached to a result that does not support the statement — which is why the retrospective audit and the invariant that every pointer resolves are both worth having.

### Rule 10: Provide public access to scripts, runs, and results

**The release checklist.** Data, or accessioned references where redistribution is not permitted; all scripts; the environment specifications at all three levels; the claim collection; the provenance records; the instruction files and skills; the hierarchical report; the reproducibility report; and a root script that rebuilds everything. Plus the two safety checks: a secrets scan, and explicit confirmation that every included data file may lawfully be published.

**Publishing the negative space.** The alternatives explored and abandoned are, in this setup, already in the claim tree with their scripts intact, which removes the main practical reason they have never been published: assembling them used to be work. Publishing them changes what a reader can assess — from "does this analysis run" to "was this a reasonable analysis among the ones that were tried". We regard this as the most consequential single change the setup makes possible.

**Archival versus development hosting.** A repository host is where the work lives; it is not an archive. Deposit a citable, versioned snapshot with a persistent identifier at publication, and reference that in the paper.

### A proposed comprehensive agentic AI setup to cover all rules

This section states the arrangement completely enough to implement it.

**The unit: a claim.** A claim is a question the project sets out to explore, written as one or two sentences of plain text, together with the analysis addressing it. It is not an assertion. **What the node's analysis yields is recorded at the node as an answer, and it is those answers, not the node text, that populate the claim collection of Rule 9. The single word does double duty across the two sections, and the working distinction is simply that a node's claim is interrogative and a Rule 9 claim is declarative.**

**The two relationship types, precisely.** The relationship type is a property of a node's whole set of children, not of individual edges — otherwise the rule for alternatives below would contradict the rule for sub-analyses within a single node. Where a question genuinely needs both, interpose a node: make the alternatives the children of a dedicated node, and let that node be one sub-analysis child among others.

***Type 1 — sub-analyses (the basic case).*** The children are supportive sub-analyses of the analysis the parent represents. Each child claim covers a sub-part of a parallel or sequential approach to the parent claim. The parent's main script calls **every** child's main script, in the order the approach requires, together with calls to the scripts stored at the parent — typically the ones that combine what the children produced. **Nesting these gives a decomposition of the overall question into progressively finer sub-questions, which is what makes it possible to say which part of the execution served which aspect of the overall claim.**

***Type 2 — alternatives.*** The children are alternative paths explored for the parent claim. Each child claim represents one possible interpretation of the parent claim, or one possible solution strategy for it. Exactly one child is annotated as the main analysis path. **The parent's main script then only calls that child's main script.** It does nothing else and the node stores no scripts of its own: an alternatives node is a pure switch, and its whole content is the question, the set of answers attempted, and the record of which was taken. **This is the structural provision for the veridical requirements: the judgment calls a stability analysis perturbs are written here as runnable siblings rather than described in prose.**

**Node contents.** Each node is a directory holding, at minimum:

| Path | Contents |
|---|---|
| `claim.md` | The analytical aim as text; the relationship type of this node's children; for alternatives, which child is the main path; a note of any environment override. Once the node has been run, the answer(s) it yielded. |
| `run.sh` | **The main script.** A short list of shell lines: calls to the main scripts of this node's children, and calls to the scripts stored at this node. |
| `scripts/` | Every script file used by this node's own analyses. May be a `scripts.zip` at archival (see below). |
| `results/` | What this node's analyses produced, including intermediates (Rule 5) and plot data (Rule 7). |
| `env/` | Present **only** where this node needs something beyond the full analysis's main environment. |
| `provenance/` | The per-result records of Rule 1 for results produced at this node. |

Children are subdirectories. Nothing about the scheme requires these exact filenames; what matters is that each node has exactly one entry point, that the entry point's calls are visible as text, and that the node's address is stable.

**A worked skeleton.** For the illustrating case of this paper:

```
root/                    "Do region sets A and B co-occur more than expected by chance?"
│                        children: sub-analyses
├── 01_prepare/          "What are the comparable region sets to analyse?"
│   │                    children: alternatives — main path: a_strict
│   ├── a_strict/        "…under the strict filtering convention"
│   └── b_permissive/    "…under the permissive filtering convention"
├── 02_measure/          "By what measure should co-occurrence be quantified?"
│   │                    children: alternatives — main path: a_jaccard
│   ├── a_jaccard/       "…as set overlap"
│   ├── b_basepair/      "…as shared base pairs"
│   └── c_distance/      "…as nearest-neighbour distance"
├── 03_null/             "Against what null is 'more than expected' judged?"
│   │                    children: alternatives — main path: a_uniform
│   ├── a_uniform/       "…uniform shuffling within the analysis region"
│   └── b_matched/       "…shuffling matched on region length and chromosome"
└── 04_stability/        "How far does the answer survive the reasonable alternatives?"
                         children: sub-analyses
```

`root/run.sh` calls `01_prepare/run.sh`, `02_measure/run.sh`, `03_null/run.sh`, `04_stability/run.sh` and then its own script that states the headline answer. `02_measure/run.sh` is one line: it calls `a_jaccard/run.sh`. The two other measures sit beside it, complete and runnable, and are not touched by the main path.

**Where the alternatives actually get run.** They get run by the stability node, whose scripts call the main scripts of the non-main siblings directly, then compare what comes back. This makes the veridical work a *part of the tree* rather than a separate exercise, and it gives the trade-off of the previous section a concrete shape: cut the stability node under a computational budget and the main path still reproduces the reported result, with the alternatives still on record as unexecuted paths. What was and was not run is then a visible decision rather than an absence.

**What a PCS stability analysis requires of the tree.** **Three properties have to hold, and each is a design obligation rather than something that comes for free. (i) *A shared output contract per fork.* All children of an alternatives node must produce output of the same shape and meaning, since downstream nodes have to consume any of them interchangeably. Where an alternative genuinely changes what is produced, the fork has been placed too low in the tree and should be moved up to a parent whose output is common to both. (ii) *A computed conclusion.* The reported conclusion must be produced by a script at the root, from files, rather than asserted in prose, so that it can be recomputed once per combination of alternatives and the results compared. (iii) *An enumerated perturbation set with a budget.* Which forks are varied, and over which of their children, must be stated in advance, because the number of combinations is multiplicative in the number of forks. The stability node holds this enumeration, runs what the budget allows, and records what it did not run. Given all three, running the root in stability mode returns a distribution of conclusions over reasonable analyses rather than a single conclusion — which is what the stability pillar of PCS asks for, and it also grounds the predictability pillar to the extent that held-out evaluation is one of the nodes.**

**Promoting an alternative.** When an alternative turns out to be the better path, the change is an annotation — the main-path marker moves, and the parent's one-line main script now calls a different child. Because this is a commit like any other (Rule 4), the history records that the switch happened and when, which is exactly the kind of decision that otherwise disappears.

**Environment resolution.** The full analysis has one main environment, specified at the root and used generally. A node's `env/` overrides or extends it for that node, and by convention for its subtree unless a descendant overrides again. Keep overrides rare and justified: each one is an environment a reproducer must build, and the reason for it belongs in `claim.md`.

**Verification of the root.** The property that makes the discipline worth it is that one script at the root reproduces everything, checkable automatically from a clean environment. Run it on a schedule, not only at submission: it is how you find out that an upstream dependency changed while you were still writing.

**Archival form.** At release, a node's `scripts/` may be stored as a zip. Do this only at release: a zip is opaque to diffing and to version control, so during development the folder is what you want, and the zip is a packaging step.

**Why claims rather than steps.** Organising by analytical aim rather than computational step is what makes the alternatives relationship meaningful: two children are comparable because they answer the same question differently. A step-organised pipeline has no natural place to record the pipeline you decided against. It also aligns the tree with the claim collection of Rule 9, so the chain from a sentence in the paper down to a command runs through a single structure.

**How the tree carries each rule.** Rule 1: the node path is the stable address a provenance record points at. Rule 4: the tree is one repository, and a node's scripts and `claim.md` are versioned together. Rule 5: intermediates live in the `results/` of the node that produced them, so their place in the analysis is given by where they sit. **Rule 8: the tree supplies the upper levels of the hierarchical report, with the within-result detail levels supplied by each node itself — see the Rule 8 appendix on why these are two hierarchies and not one.** Rule 9: claims attach to nodes. Rule 10: the release is the tree, alternatives included.

**Where this setup is a poor fit.** Analyses dominated by a single very long computation, workflows already governed by a mature workflow manager, and collaborative projects with an established structure are all cases where imposing this tree would cost more than it returns. The transferable parts — provenance records, the claim collection, the invariant checks, the clean-room verification — do not depend on the tree.

### Validating that the rules were actually followed

**A starting set of invariants.** Every file under `results/` has a provenance entry. Every provenance entry references an existing script, commit and environment. Every plot has a data file and a plotting script beside it. Every claim resolves to at least one existing result. Every stochastic script has a recorded seed. The working tree was clean at the point each result was produced. No value passes between steps except through a file. Each is a few lines of code and fails loudly.

**Running the outsider test well.** Give the fresh agent only what a reader would have — the repository and its instructions, no conversation history. Ask it to *do* the thing, not to evaluate the documentation; a system asked whether instructions are clear will tend to say yes, whereas a system asked to follow them will visibly fail at the ambiguous step. Record what it got wrong, fix the documentation, repeat. The failure modes it surfaces are almost always assumptions you did not know you were making.

**Scheduling.** Invariant checks belong on every commit and at the end of every analysis; the clean-room rebuild on a schedule and before release; the outsider test after any substantial change to the instructions and before release. None depends on anyone remembering, which is the entire point.

**What validation cannot do.** These checks confirm that the record is structurally complete, not that it is true. A provenance entry can point at the wrong script, and a claim can point at a result that does not support it. Structural checking narrows where a human must look; it does not remove the need to look.

### Trade-offs

**Making the token/effort trade-off explicit.** The failure mode is expansion without decision: because each request is individually cheap, a project drifts into tracking everything at maximum fidelity, or exploring perturbations nobody will read. State the intended level in the instruction file — what is tracked, at what granularity, with what verification cadence — so it is a decision rather than a default.

**Criticality annotation, concretely.** For each stored artifact, a small record: main or side result; regenerable or not; roughly what regeneration costs in compute and wall-clock; how important for transparency. An agent can produce these at scale from rough judgment, and they need only be roughly right. Their value is making later pruning a targeted operation instead of a panic, which preserves the option of keeping everything for as long as it is affordable.

**Budgeting robustness.** Enumerate the judgment calls, estimate the cost of perturbing each, rank by expected informativeness, and cut at the budget line — recording where the line fell and what was below it. A stability analysis that stopped for budget reasons and says so is far more useful than one that silently explored whatever happened to be quick.

### Generically useful agentic skills for reproducibility

**The initial set.** One skill per rule: provenance recording and result binding; the edited-copy convention with diff tracking; environment pinning with clean-room verification; result-tied commits with instruction versioning; intermediate storage with format selection; exhaustive seeding with a re-run check; plot data capture; hierarchical report generation; claim-collection maintenance and text-to-claim auditing; and release assembly with secrets and permission scanning. Supporting skills: the invariant checker, the outsider-test harness, the criticality annotator, the perturbation planner, and the reproducibility report generator.

**Curation model.** Worth borrowing from community-curated workflow collections, of which nf-core [12] is the clearest example: a required structure per contribution; a stated purpose and motivation, so a user can tell whether a skill matches their setting; review by people other than the author; versioning, so a project can pin the skill version it used, which matters because a skill is part of the method (Rule 4); and explicit security review, because an instruction module is executable influence over someone else's agent and repository. We would like to see this grow into a properly governed collection, and intend to seed it with the skills accompanying this paper.

**The reproducibility report.** Inputs: the final text, the claim collection, the claim tree, the provenance records. Output: a document stating what was produced, what is tracked and how, a provenance graph from statements down to commands, and the veridical section — alternatives explored, basis for choices, stability of conclusions. It should degrade gracefully: run on a project that followed none of these rules, it should report honestly on what little can be established, which is itself a useful diagnostic.

### An illustrating case

**Full specification.** The case is a co-occurrence analysis on public genomic region sets: given two sets of genomic regions, do they overlap more than expected by chance? It is chosen because it is computationally light, because the data are freely redistributable, and — decisively — because the answer is known to be sensitive to choices that all look reasonable, which makes it a case where the veridical apparatus has something real to report rather than a formality.

The perturbation space covers three families of judgment call: the co-occurrence measure; the null model against which "expected by chance" is defined; and the preprocessing upstream of both, such as how region sets are filtered and how the analysis region is delimited. The main path is one defensible combination; the alternatives are siblings in the claim tree, run and retained rather than discarded.

The claim collection contains the headline claim about co-occurrence, the stability claim about how far it survives the alternatives, and the supporting claims underneath each — every one bound to stored results. The manuscript section describing the case is itself written through the two-step process of Rule 9, so that the paragraph a reader is reading traces back through a claim to a result to a command.

**What the case is meant to demonstrate.** That the apparatus is affordable on a small project; that the negative space is worth publishing; that the invariant checks and the outsider test catch real problems; and — if it turns out that way — where the setup was more trouble than it was worth, which is as useful a finding as the others.

---

#manuscript #reproducibility #agentic-ai #veridical-ai #vds
