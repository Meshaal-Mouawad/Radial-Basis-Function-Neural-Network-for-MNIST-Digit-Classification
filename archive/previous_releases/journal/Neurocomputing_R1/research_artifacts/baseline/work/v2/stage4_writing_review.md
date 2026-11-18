# Stage 4 — Independent academic writing and evidence review

**Decision: PASS.** The corrected manuscript presents one coherent, evidence-supported claim: training-derived quantities can certify equality between a Gaussian ridge RBF classifier's prediction and its nearest-prototype label over a complete width–penalty region. All identified material writing, notation, attribution, and evidence-description defects were corrected and rechecked. No unresolved CRITICAL or MAJOR issue remains in this review's scientific and writing scope.

Review date: 6 November 2026. The complete `upload/Universal_Academic_Writing_Agent_Prompt_v2(1).md` and the user's academic instructions governed this review. Selected model/reasoning: inherited agent configuration, retained for continuity with the independent theorem and executable audit. This reviewer is separate from the manuscript writer. Argument, clarity, evidence, and cold-reader checks were sequential passes by this reviewer, not four separately recruited reviewers. The reviewer did not edit the manuscript or run a new study.

## A. Authoritative text and argument baseline

Reviewed files: `work/v2/manuscript/main.tex`, `results.tex`, and `references.bib`. Evidence baseline: the frozen protocol and executable, all archived predictions/masks and separately released evaluation labels, the independent theorem review, completed-output audit, and the descriptive analysis tables. The final reviewed build has 16 pages and 12 resolved references. Its build log contains no warning, overfull-box, or undefined-reference line.

| Argument component | Manuscript realization | Assessment |
|---|---|---|
| Problem | A nearest selected example's class need not equal a Gaussian RBF's learned readout class. | Identified in the first introduction paragraph and explained through the output rule. |
| Gap | The target operation is a training-derived guarantee for a family with varying Gaussian width and ridge penalty. | Distinguished from architectural interpretation, sample influence, input/label perturbations, and fixed-design regularization-path bounds. |
| Response | Exact reference residual; nonnegative class-pair majorants; prototype-block spectral floor; penalty supremum; query margin test. | Defined before use and connected in one derivation. |
| Evidence | Proof, bound hierarchy, separate synthetic verification, frozen two-dataset experiment, and independently reconstructed counts. | Appropriate evidence is assigned to each claim. |
| Contribution | A computable pre-fit continuous-region label-agreement guarantee, with demonstrated coverage relative to a norm/count comparator. | Matches title, abstract, introduction, discussion, and conclusion. |

The title names the mathematical object and model. The abstract states the operation, proof mechanism, measured coverage, identical sharp/basic masks, zero coverage at the other endpoints, and the exact finite-check denominator. The introduction supplies purpose and intuition before the matrix definitions. No companion paper is required to understand the certificate or experimental results.

## B. Research question–method–evidence alignment

| Question or objective | Method | Evidence in the manuscript | Resolution |
|---|---|---|---|
| Can training and query information certify the complete width–penalty region without fitting the output weights? | Residual lemma, spectral lower bound, exact penalty-majorant supremum, strict query margin. | Sections 3–4 and Theorem 1, with complete proofs. | Answered analytically. The finite grid is used for implementation checks. |
| What is gained by retaining class-specific overlap and sharpening the penalty envelope? | Identical-region sharp, basic, and cancellation-aware Frobenius bounds; theoretical ordering and matched masks. | Proposition 2; 587,703 sharp/basic certified query-region cases versus 285,286 Frobenius cases; identical sharp/basic masks. | Distinguishes proved bound improvement from realized coverage improvement. |
| Where does the certificate produce useful coverage? | Seven width endpoints, three penalty floors, three nested budgets, five seeds, both datasets, retaining every declared condition. | Table 2, Figure 1, and complete archived grid tables; positive coverage only at the narrowest scaled endpoint. | Reports successful and zero outcomes, including zero-coverage seeds and 102 inapplicable regions. |
| How do certificate coverage, observed label agreement, and class accuracy relate? | Separate metrics with explicit denominators, fitted endpoint labels, and held-out targets. | Figure 2 and Section 6.2; broader-width accuracy and label agreement are both reported. | Avoids interpreting agreement as true-label correctness or claiming an accuracy innovation. |
| Does the implementation conform to the analytic statement at declared probes? | Frozen masks and predictions, nine finite probes per region, independent reconstruction. | 5,289,327 sharp checks; 13,146,228 method-tagged checks; zero observed violations; 480 factorizations and 2,880 readouts. | Counts are correctly identified as repeated-query verification workloads. |

The mathematical review confirms the residual signs, the non-prototype restriction in P, clipping before squaring the eigenvalue floor, the exact supremum of the selected majorant, the strict class-margin logic, and the three-bound hierarchy. The theorem quantifies finite penalties. The appendix's small-width limit includes the necessary duplicate-coordinate condition and labels its counterexample as constructed.

## C. Issue register and verified closure

Locations below use stable section/equation identifiers because final float placement changed line numbers.

| ID | Severity when found | Location and defect | Required correction | Closure and scientific effect |
|---|---|---|---|---|
| W1 | MAJOR | Frobenius bound, `eq:frobenius`: `eta_t^2` lacked the LaTeX backslash and rendered an incorrect symbol. | Restore `\eta_t^2`. | Fixed in source and inspected in the rendered equation. Restores the intended, independently validated formula. |
| W2 | MAJOR | Section 3.3 said reference weights preserve prototype labels, which could imply a prediction guarantee under arbitrary overlap. | Describe the coefficient row explicitly: one scaled own-class coefficient and zero other-class coefficients. | Fixed. The theorem remains the source of the prediction guarantee. |
| W3 | MAJOR | Residual proof referred to normal equations for W0 even though W0 is a reference matrix. | Use `G W = H^T Y` and the residual definition directly to obtain `G(W-W0)=R`. | Fixed and inspected in the rendered proof. Removes a false explanatory premise without changing the valid algebra. |
| W4 | MAJOR | Evaluation implementation text called the archived minimum margin guarded. The executable saves raw `lhs-rhs` and applies the guard separately. | Say minimum raw class-pair margin. | Fixed; agrees with `certificate_min_gaps` and the executable audit. |
| W5 | MAJOR | Initial softmax-paper attribution used Xiao and an obsolete citation key. | Use Fazaeli-Javan and Ghiasi-Shirazi, `fazaeli2026`, consistently in prose, table, and bibliography. | Fixed everywhere. Primary publisher metadata and the current claims were checked independently. |
| W6 | OPTIONAL | Abstract percentages did not explicitly name averaging over seeds. | Identify the percentages as means. | Fixed. Preserves the verified numerical values and clarifies aggregation. |
| W7 | OPTIONAL | First build let the related-work table interrupt model development and result floats extend into Discussion. | Adjust float placement and keep result floats before Discussion; improve the comparison table's text alignment. | Root applied production-only float and table alignment changes and rebuilt the final 16-page artifact. |

An unfinished results placeholder seen in the first live draft was replaced by the complete results section before the substantive review closed. It is absent from the final source. The scientific record, experiment protocol, data, predictions, and masks were not changed during writing review.

## D. Structure, readability, source, and visual checks

The paragraph review found identifiable topics, developed explanations, relevant proof or evidence, and completed implications. Definitions and proof steps use the amount of space their mathematical function requires. The prose avoids imposed paragraph templates and ornamental transitions. The connected treatment of geometry, labeled non-prototype inputs, and query margins should be retained. The discussion explaining equal sharp/basic masks is particularly necessary: it identifies the precise empirical contribution of the class-wise information without assigning a measured gain to the sharper envelope.

The cold-reader check can recover the problem, inputs, output, model objective, computational steps, theorem assumptions, evaluated conditions, observed results, and added capability from the manuscript alone. The constructed duplicate example develops the role of non-prototype labels. The limitations are consolidated in one final main-text section. Essential mathematical definitions remain at the point needed to interpret the theorem; negative experimental findings remain in Results.

All 12 citation keys resolve to bibliography entries, with no unused bibliography entry. High-risk recent-literature descriptions were independently checked against publisher material: the softmax paper's sample-weighted positive/negative prototypes and near-boundary-sample finding; Gaussian KAN first-layer conditioning and scale selection; and partition-of-unity normalization and constant reproduction. The comparison to safe regularization paths was checked against the primary paper's setup and its Section 4, Lemma 4, and Proposition 7. The stated distinction is supported: the present feature matrix changes with width, and the target is nearest-prototype label agreement over the two-parameter region.

Source checks:

- [Fazaeli-Javan and Ghiasi-Shirazi, 2026](https://doi.org/10.1016/j.neucom.2026.133904): publisher metadata, abstract, introduction, and accessible section excerpts.
- [Noorizadegan, Wang, and Ling, 2026](https://doi.org/10.1016/j.neucom.2026.134771): publisher metadata, abstract, selected scale-analysis text, and conclusion.
- [Noorizadegan, 2026](https://doi.org/10.1016/j.neucom.2026.135408): publisher metadata and abstract.
- [Ndiaye et al., 2019](https://proceedings.mlr.press/v97/ndiaye19a/ndiaye19a.pdf): primary proceedings paper, especially the fixed-design setup and safe-region validation argument.

The reviewer visually inspected both original figure images and every page of the corrected 15-page scientific build, including the corrected equations, table values, figure legends/captions, and references. Figure 1 displays every scaled endpoint, all floors and all seeds, including zero outcomes; Figure 2 clearly separates endpoint agreement and class accuracy. The final 16-page build differs through table alignment and float placement, and its source/build checks pass. Root completed the final whole-document production inspection of that pagination; `work/v2/PRODUCTION_VERIFICATION.json` records PASS and matching final source/PDF hashes. This reviewer read that record and checked its hashes against the files reviewed here.

| Acceptance gate | Status | Evidence |
|---|---|---|
| Single coherent claim across sections | PASS | Argument map and full-text read. |
| Complete proof and correct contribution scope | PASS | Independent theorem review plus source/rendered-equation closure. |
| Research questions supported by methods and evidence | PASS | Alignment table above and frozen result reconstruction. |
| Correct denominators and negative findings | PASS | All endpoint/certificate CSV counts independently reproduced. |
| No unsupported causal-explanation or accuracy-novelty claim | PASS | Abstract, introduction, discussion, conclusion, and limitations read together. |
| Developed paragraphs and first-reader independence | PASS | Sequential clarity and cold-reader passes. |
| Material review fixes closed | PASS | Six textual/notation checks plus final citation and placeholder checks. |
| Citations resolve; closest-work descriptions supported | PASS | Twelve resolved keys and primary-source checks described above. |
| Figures and scientific equations readable | PASS | Original figure images and all pages of the corrected scientific build inspected. |
| Final 16-page production inspection | PASS (root verification) | Final source and log checked here; completed final-page inspection and matching hashes are recorded in `PRODUCTION_VERIFICATION.json`. |

## Final reviewed artifact identities

- `main.tex` SHA-256: `316a3ae98549cff890489a6c7888daea6e339fa3e98da5e4ccdf2db4667d017f`
- `results.tex` SHA-256: `6d1b2b0907d6cd09331a329da3261b9f5eaf541cd292398fe8400d5dfd38acd1`
- `references.bib` SHA-256: `4c87c2ec1cb0e79999b39cb4fdde2c511d3babb72d763b7e584ebdf1e077d03f`
- `main.pdf` SHA-256: `a06a48e271c44f063cce74a2609fffe346be6093ec12a3157cec5a93cfc4d251`

## Review scope

This is the requested independent writing/scientific-evidence stage. Journal acceptance, publication eligibility, author declarations, and final upload decisions belong to the subsequent editor and submission stages. The record distinguishes real-arithmetic proof, guarded floating-point evaluation, and finite-probe checks consistently. No new experiment or production-model fit was performed for this review.
