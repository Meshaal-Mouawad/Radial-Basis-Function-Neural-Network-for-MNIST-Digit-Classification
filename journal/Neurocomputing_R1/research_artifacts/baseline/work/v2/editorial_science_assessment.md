# Independent scientific contribution assessment: v2

Review date: 6 November 2026. Reviewer role: independent GOLD scientific/editorial challenge. The complete `project_sources/03-GOLD_NICHE_JOURNAL_CHIEF_EDITOR_PROMPT_v1.md` was read before this decision. This report evaluates the new theorem and completed experiment; the integrated manuscript and rendered submission package require their subsequent final review.

## Decision

**G2 — PASS for a training-derived sufficient certificate of nearest-prototype label agreement over a continuous Gaussian-width interval and an unbounded ridge-penalty interval.** The v2 work supplies the explanatory condition missing from v1, gives a proof, implements the condition without fitting a readout, and measures its coverage against two comparators with identical certificate semantics. The independent mathematical and implementation audits pass. This is a substantive change from the v1 paper's characterization of known bandwidth behavior.

**Scientific journal fit — FIT for a theoretical/methodological Neurocomputing research article.** The official scope expressly includes theoretical understanding of neural networks and learning systems. The completed contribution addresses a precise decision property of Gaussian RBF networks. Its scientific adequacy rests on that property and its finite-parameter guarantee, rather than on classification-ranking performance.

No further experiment is required to establish the stated contribution. A concise prior-work attribution to safe regularization-path inference must be incorporated into the manuscript, and the complete zero-coverage and equal-mask findings must remain visible. The manuscript writer and lead editor have received those specific integration requirements.

## Paper identity and argument

The author is Meshaal Mouawad. The working title is *Training-Derived Regions of Nearest-Prototype Agreement in Gaussian RBF Classifiers*. This is a theory paper with controlled computational evaluation. The unchanged April 10 report and repository commit `fc7ff848d10b7f060e028b2271fbfc9ce8687798` are historical evidence. The present theory and prospective experiment were developed and executed on November 6, 2026. Submission has not occurred.

The authority order for this review is the theorem and frozen executable, immutable prediction archives and completed-output audit, verified original research, prior editorial decision, and official venue scope. I read `work/stage5_gold_review.md`, `work/v2/PAPER_IDENTITY_AND_PLAN.md`, the complete `work/v2/theory.md`, the complete independent mathematical review, the frozen protocol and completion record, production certificate code, implementation audit, evidence report, and analysis summary. I independently recomputed central summaries from both result CSVs without changing them.

The scientific argument is:

- **Problem:** A nearest selected prototype provides a simple label, while an unconstrained learned readout can produce a different label.
- **Existing ability:** Prototype architectures, sample-influence analyses and optimization-based safe regions already analyze or control prediction behavior.
- **Question:** For fixed inputs, labels and selected training prototypes, can training-derived quantities certify the nearest-prototype label simultaneously for every `0 < sigma <= t` and every finite `lambda >= lambda0`?
- **Response:** Use the prototype-label reference readout, retain class-specific overlap terms in its exact normal-equation residual, bound the inverse through the selected-prototype block, and maximize a residual majorant at two penalty endpoints.
- **Evidence:** A sufficient-condition proof; independent algebraic and synthetic verification; a frozen two-dataset, five-seed, three-budget study; complete archived predictions and masks; independent reconstruction of all reported counts.
- **Contribution:** A computable, query-specific sufficient parameter region in which the RBF classifier and nearest-prototype label agree, together with measured coverage and conservatism of that region.

## Closest-prior-work challenge

The following distinctions are my comparison of the actual research objects. They are not attributed to the prior authors as their own descriptions of an unresolved problem.

| Closest work and primary link | Verified prior capability | Relationship to the present operation | Access and exact location |
|---|---|---|---|
| Saralajew, Rana, Villmann and Shaker (2025), *A Robust Prototype-Based Network with Interpretable RBF Classifier Foundations*, AAAI, DOI [10.1609/aaai.v39i19.34233](https://doi.org/10.1609/aaai.v39i19.34233); [author full text](https://arxiv.org/html/2412.15499v3) | Explains why unconstrained RBF weights can break correspondence between closest components and class decisions. Develops a probabilistic component architecture and input-perturbation robustness bounds. | Supplies the direct motivation. The present classifier retains an unconstrained ridge readout and certifies agreement as width and penalty vary, with query and training set fixed. | Author version v3, Sections 2–3, Theorem 1, Discussion. Relevant full sections inspected. Web retrievals `turn82view0`, `turn85view0`, `turn90view2`. |
| Fazaeli-Javan and Ghiasi-Shirazi (2026), *Sample-based interpretability of softmax neurons via learned prototypes*, Neurocomputing 694, 133904, DOI [10.1016/j.neucom.2026.133904](https://doi.org/10.1016/j.neucom.2026.133904) | Uses positive/negative learned prototypes to analyze Softmax-neuron training-sample influence and the role of near-boundary observations. Experiments include MNIST, Fashion-MNIST and FERET. | Establishes current same-journal interest in prototype/sample decision analysis. Its stated object is Softmax-neuron formation; the present object is a fixed selected-prototype Gaussian ridge family. | Publisher-indexed abstract, full introduction, section excerpts and authorship statement inspected; direct publisher opening returned 403. Retrieval `turn95search0`. The authorship statement supports the two names above; an inconsistent DBLP search key must not override it. |
| Noorizadegan, Wang and Ling (2026), *Making Gaussian Kolmogorov–Arnold Networks Reliable and Accurate*, Neurocomputing, article 134771, DOI [10.1016/j.neucom.2026.134771](https://doi.org/10.1016/j.neucom.2026.134771); [author v3](https://arxiv.org/html/2604.21174v3) | Connects first-layer feature geometry with Gaussian scale choice and establishes a practical operating interval supported across approximation/PDE settings. Section 6 identifies further classification investigation as future work. | Prevents treating scale–conditioning analysis as an unresolved general topic. The present theorem addresses a label-equivalence property of a different model and objective. | Author v3, August 12, 2026, abstract and Sections 1, 2, 6 inspected; publisher online date August 10 verified. Retrievals `turn96view0`, `turn97view1`, `turn97search0`. Earlier author versions have different titles and authors. |
| Noorizadegan (2026), *Partition-of-Unity Gaussian Kolmogorov–Arnold Networks*, Neurocomputing, article 135408, DOI [10.1016/j.neucom.2026.135408](https://doi.org/10.1016/j.neucom.2026.135408); [author v2](https://arxiv.org/html/2604.23599v2) | Applies Shepard normalization to edge basis values, reproduces constants, and evaluates scale sensitivity and approximation quality. | Establishes a recent normalization-based response to Gaussian scale sensitivity. Our query rescaling preserves a fixed model's argmax; it is not the training-basis modification evaluated there. | Author full-text introduction, formulation and conclusion inspected; publisher online date October 14, 2026 verified. Retrievals `turn97view0`, `turn96view2`, `turn97search1`. |
| Ndiaye, Le, Fercoq, Salmon and Takeuchi (2019), *Safe Grid Search with Optimal Complexity*, ICML, PMLR 97:4771–4780; [publisher paper](https://proceedings.mlr.press/v97/ndiaye19a.html), [full PDF](https://proceedings.mlr.press/v97/ndiaye19a/ndiaye19a.pdf) | Uses duality gaps and safe regions to control objective and validation behavior over regularization intervals with a fixed design matrix. The classification result relates score margins to a safe ball. | Generic inference over penalty intervals predates this work. The present construction uses an explicit prototype-label reference and handles the changing Gaussian design across a width interval jointly with all penalties above a floor. | Publisher PDF, Sections 2–4, Lemma 4, Proposition 7 and Conclusion inspected. The conclusion explicitly discusses multidimensional parameter grids as future work. Retrievals `turn87view1`, `turn90view1`. |

The bounded search also retrieved Suzuki et al. (2014), *An Algorithmic Framework for Computing Validation Performance Bounds by Using Suboptimal Models*, [arXiv:1402.2148](https://arxiv.org/abs/1402.2148). Its verified author abstract already describes unknown-model inference using a suboptimal reference. Full-text access attempts failed. This reinforces the safe-inference attribution; a general claim that prediction bounds require fitting every target model would be false. Retrievals `turn86academia5`, `turn88academia7`.

The new operation survives these comparisons. The relevant evidence is the explicit difference in models, varying objects, reference construction and certified output. An unsuccessful keyword search alone is not the basis of this decision.

## Contribution–evidence matrix

| Claim | Present research operation | Direct evidence | Accepted interpretation |
|---|---|---|---|
| Agreement over the complete parameter rectangle | Derives a uniform residual bound and strict query-margin test | `theory.md`, Sections 3–6; independent mathematical review | A sufficient finite-parameter guarantee for fixed data, labels, preprocessing and selected prototypes |
| Exact supremum for the specified penalty majorant | Reduces its norm maximum to the lower endpoint and infinite-penalty limit | `theory.md`, Section 5; independent derivation | Exact optimization of this majorant; the residual and true classification discrepancy can be smaller |
| Analytical dominance of three certificates | Retains class-specific overlap vectors, then compares with basic and Frobenius/count bounds | `theory.md`, Section 5; completed constant/mask hierarchy audit | `sharp <= basic <= count` analytically, with corresponding certificate-set inclusion |
| Class-specific overlap retention changes practical coverage | Evaluates the same rectangles and query sets using all three methods | Frozen masks, complete certificate CSV, `analysis/summary.md` | Higher measured coverage than the cancellation-aware Frobenius bound; sharp and basic masks are identical in this experiment |
| Certificate preparation avoids output optimization and the full training normal matrix | Forms `P` and `Q = E.T @ (E @ Y_C)` directly | Production certificate code and operation counts | `O(N K C)` preparation after feature construction, plus prototype/pair work; no measured runtime or memory superiority claim is established |

The proof's ingredients are established linear algebra. Their use here produces an explicit finite-width guarantee that can be evaluated on a proposed region. This resolves a different knowledge question from merely observing the small-width nearest-prototype limit. The region can also abstain in configurations that defeat an unconditional limit statement, including conflicting duplicates.

The method's conservatism is quantified by the completed evaluation. That is relevant evidence about a sufficient certificate, rather than a reason to require a new accuracy-maximizing algorithm. Requiring state-of-the-art image classification or human interpretability would change the paper's research question.

## Independent result check and scientific meaning

The frozen experiment contains 30 dataset/seed/budget groups and 630 parameter rectangles. The same query sets recur across settings: 4,027 globally unused MNIST images and 10,000 Fashion-MNIST test images. I recomputed the following from the saved CSVs and checked them against the independent archive audit:

- Only the predeclared smallest scaled endpoint, `t = s_C/16`, has positive coverage. At absolute `t = 1` and all five larger scaled endpoints, every certificate has zero coverage.
- At `K = 100`, sharp/basic mean coverage across five seeds is **99.9106%** on MNIST at all three penalty floors. Fashion-MNIST coverage is **79.086%, 79.630%, and 98.656%** at floors 0, 1 and 100. The five-seed sample SDs for the first two Fashion settings are approximately 44 percentage points and must be reported or made directly available.
- Sharp and basic counts coincide in all 630 rectangles; the independent saved-array audit confirms identical masks. The sharper formula supplies an analytical refinement, with no additional observed certified queries here.
- Across all methods and repeated rectangles, 13,146,228 certified finite-probe exposures contain zero disagreements. The independent audit recomputed those exposures. The proof supplies the continuous-region guarantee.
- The smallest certified raw margin is `1.4658047523541384e-05`. The smallest ratio to the actual numerical guard is approximately **51,145**. The finite arithmetic check is well separated from the declared guard.
- At absolute width one, mean endpoint nearest/readout agreement across the declared budgets and floors remains **97.6475%** on MNIST and **98.2871%** on Fashion-MNIST despite zero certification. This is a direct measured instance of conservatism.

The strongest observed improvement is preservation of class-specific overlap information over the norm/count reduction. The complete outcome also establishes where the tested certificate stops providing information. Both findings belong in the main Results narrative.

## Minimal manuscript repairs and retain decisions

| Finding | Required integration | Severity and evidence |
|---|---|---|
| Safe inference along regularization intervals is an established predecessor | Add a short connected explanation of Ndiaye et al.; state the present simultaneous width/penalty operation precisely | Required literature precision; publisher Sections 2–4 |
| The penalty endpoint expression is sharp for a majorant | Keep the object of the exact supremum explicit in theorem, discussion and abstract wherever mentioned | Required mathematical precision; proof |
| Sharp and basic have identical empirical coverage | State this directly; associate observed coverage gains with class-structured terms versus Frobenius | Required numerical fidelity; all 630 rectangles |
| Every larger width and absolute width one has zero coverage | Keep these settings and denominators visible, including the high actual agreement at width one | Required preservation; complete frozen grid |
| Finite checks reuse queries and overlap in parameter points | Use unique evaluation-set sizes for sample description; label probe totals as verification workload | Required denominator precision; archived design |
| Real-arithmetic theorem and guarded float64 execution are separate evidence objects | State arithmetic and guard in Methods and consolidate the numerical boundary in Limitations | Required claim fidelity; independent implementation audit |
| The v1 failure concerned a missing new explanatory operation | Close that finding with the v2 finite-region theorem and coverage evidence | Resolved; do not reopen it by demanding unrelated predictive-performance improvements |

Retain the exact residual identity, prototype-block spectral floor, two-endpoint maximization, explicit strict margin, duplicate counterexample, full grid, strong cancellation-aware Frobenius comparator, immutable prior results and independently verified split chronology. No cosmetic rewrite is needed to create another contribution.

## Gate disposition for this stage

| Gate or component | Status | Decision basis |
|---|---|---|
| G1 scientific venue fit | PASS | Official scope includes theory that increases understanding of neural/learning systems; directly relevant recent journal conversation verified |
| G1 current formatting and exact institutional title eligibility | NOT VERIFIED in this review | Separately tracked venue/administrative checks; no bearing on the mathematical result |
| G2 contribution | PASS | Exact finite-region operation survives the stated closest-work comparison and is supported by proof and measured nonzero coverage |
| G5 source support for this assessment | PASS | Claims are restricted to inspected original-paper passages and recorded access levels |
| G6 theorem and completed protocol | PASS | Independent derivation, frozen inputs/source, valid comparators and full grid |
| G7 central results | PASS | Independent CSV recomputation plus full saved-array audit; adverse and null results retained |
| Full-manuscript G3–G4, G8–G11 and final closure | NOT VERIFIED at this stage | Integrated manuscript, final figures, citations, source/PDF identity and package await the requested subsequent review |

**Stage outcome: COMPLETE.** The specific v1 G2 blocker is closed by v2. Proceed with unified manuscript integration and full GOLD review.

## Limitations of this assessment

This is an early scientific decision on the completed research, not a publisher acceptance decision. The literature search is bounded and purposive. Relevant author-version sections were inspected for the Gaussian-KAN comparisons; the final publisher typeset papers were not fully retrieved. The Softmax comparison uses publisher-indexed introduction and excerpts, so an unobserved full-text theorem is not represented as definitively absent. The claim is therefore framed through the positive capability established here and the verified scope of close predecessors. The numerical evidence uses float64 with a strict guard, without outward-rounded interval verification. The two datasets and random prototype designs establish the reported coverage for those conditions. Final manuscript readability, production and submission-specific requirements remain assigned to the subsequent full review.

## Official venue source

Elsevier, [Neurocomputing scope](https://shop.elsevier.com/journals/neurocomputing/0925-2312), accessed 6 November 2026. Relevant scope paragraphs inspected directly, retrieval `turn82view2`, lines 92–99. The scope welcomes theoretical understanding of neural networks and learning systems; it does not impose a universal state-of-the-art accuracy condition on theory articles.
