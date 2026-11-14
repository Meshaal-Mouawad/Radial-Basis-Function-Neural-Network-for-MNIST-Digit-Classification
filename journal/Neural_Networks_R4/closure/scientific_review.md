# Independent scientific review of R4

**Decision: R4 is scientifically coherent and ready for independent specialist review. No blocking scientific error or mandatory numerical correction was identified. Its significance for Neural Networks is borderline: the supported contribution is a focused analysis of continuous decision persistence, with a thorough empirical account of its operating limits.**

Reviewer configuration: **GPT-6 Astra, High reasoning**, explicitly configured as `model=gpt-6-astra`, `reasoning_effort=high`, `fork_turns=none`, as confirmed by the lead agent's spawn record. Review date: 14 November 2026. This review makes its own scientific judgment from the manuscript and evidence; the earlier production PASS markers do not determine this verdict.

## Paper identity and argument

The reviewed manuscript is Meshaal Mouawad's *Training-Derived Regions of Nearest-Prototype Agreement in Gaussian RBF Classifiers*, R4, in `working_R4/source/`. The intended reader works on RBF models, prototype interpretation, or mathematical analysis of neural classifiers. The scientific genre is a theoretical methods paper with empirical diagnosis. The recorded target is Neural Networks; no journal submission is recorded here.

The research problem is specific: a conventional Gaussian RBF classifier combines all prototype responses through a learned ridge readout, so the nearest prototype's label can differ from its fitted label. The study asks when their equality persists throughout a prescribed two-parameter family. It supplies training-derived sufficient conditions, strict exclusion witnesses, and local-band penalty-tail conditions. Proofs establish continuous guarantees; archived image experiments measure coverage, competing regimes, class composition, and sampled path behavior. The contribution is the computable decision-region analysis and the resulting empirical separation between persistence and predictive accuracy.

The authoritative evidence used was the integrated R4 source, the saved-data work plan, the R4 revision report and source-consistency record, the four independent numerical-verification receipts, the independent numerical audit, and the adopted chief-editor protocol. R3 and the original results were treated as preserved baselines. No manuscript source or numerical result was changed.

## Mathematical assessment

| Result and location | Independent reasoning | Assessment |
|---|---|---|
| Residual decomposition, `main.tex`, “An exact readout residual” | Expanding H=S+E gives HᵀH=I+2E_C+EᵀE because the selected prototype block is symmetric. Subtracting the prototype-label reference cancels Y_C and produces the stated coefficients of V, P, and Q. | Valid |
| Spectral floor, `main.tex`, “A bound for the entire parameter region” | The selected rows lower-bound HᵀH by BᵀB. The positive Gershgorin bound applies when β<1; clipping before squaring gives the correct zero floor otherwise. | Valid |
| Exact penalty envelope, same subsection | The nonnegative majorant lies below the convex combination of its value at the penalty floor and its limiting vector. Both endpoint norms are attained or approached, establishing the stated supremum of that majorant. | Valid |
| Full-width agreement theorem, `main.tex`, “From a class-pair bound to a label guarantee” | Distance-gap normalization preserves labels and is monotone in width. The retained nearest response lower-bounds the reference margin, and Cauchy–Schwarz bounds the fitted perturbation. Strict inequalities produce a unique winning class throughout the declared family. | Valid |
| Bound hierarchy and nesting, `main.tex`, “Comparators and nested certified regions” | Entrywise domination proves sharp≤basic; Frobenius inequalities prove basic≤norm/count. Endpoint quantities and the spectral denominator have the required monotonic directions. | Valid |
| Large-penalty exclusion, `ridge_theory.tex`, Proposition “Large-penalty decision and exclusion” | The resolvent identity gives the stated 1/λ correction bound. A strictly positive competing limiting margin therefore supplies a finite disagreement tail and excludes every requested region containing that width and an unbounded penalty interval. | Valid |
| Signed local certificate, `ridge_theory.tex`, Theorem “Local-width, large-penalty agreement” | Nonnegative endpoint matrices and signed splitting correctly enclose Aσvσ. The resulting norm bound and limiting-vote margin establish positivity uniformly over the local interval and tail. At equal endpoints the enclosure becomes exact. | Valid |
| Constructed examples, `exact_ridge_examples.tex` | The displayed Gram matrices, class-difference vectors, and 2×2 inverse numerators are consistent. The strict-reversal and tied-limit cases exercise distinct logical cases. | Valid |

The mathematics establishes a real analytical capability. The two-endpoint result exactly removes penalty maximization from the selected bound, and the signed interval construction extends the available region geometry. The proofs support these claims without requiring empirical predictive improvement.

## Question–evidence–finding assessment

| Scientific question | Evidence examined | Supported finding |
|---|---|---|
| Does retaining class-wise training structure improve certification? | Bound hierarchy; original coverage table; dense-frontier results | The class-wise bounds substantially improve coverage over the norm/count comparator. Sharp versus basic gains appear in 35 of 6,030 dense-grid conditions and remain absent in the original grid. |
| Where do sufficient coverage and identified family failure occur? | Full-width theorem; region partition; frontier and original witness results | Loss of sufficient coverage precedes widespread identified disagreement. The unresolved category retains its exact logical meaning. |
| Does certification reach competitive archived models? | `r4_methods.tex`, competitive design; `r4_results.tex`, competitive results; independent competitive receipt | All 328 models retained by the primary validation rule have zero sharp full-width coverage. The 494-model and 116-model sensitivity sets give the same result across all 30 groups. |
| Does a sufficient tail bound describe sampled onset? | Path definitions and complete path audit | The 190,405 returns among 3,366,480 query–width paths demonstrate sampled nonmonotonicity. The manuscript correctly separates first sampled detection, returns, and the sufficient disagreement tail. |
| Does certified-subset accuracy establish advantageous selection? | Matched cardinality comparisons; class counts; independent composition receipt | Agreement-gated distance selection has higher mean accuracy in three settings and identical selections in the fourth. MNIST's constant class-1 endpoint produces 10% selected-class macro accuracy across ten represented true classes. These comparisons support the stated composition diagnosis. |
| How much do limiting witnesses add to finite probes? | Exact overlap records; fixed-order replay; independent path/probe receipt | Incremental exclusions are measured against the specified probe bank. Expanded probes recover at least 95% of the original limiting set after mean 15.6 and 20.2 checks at the stated endpoint; the manuscript reports replay counts. |
| Does increasing budget improve the selected finite models? | Validation selection and paired budget/cross-seed records | Evaluation accuracy improves at each budget step in every seed; the paired gains and cross-seed overlaps are descriptive outcomes on shared evaluation images. |

The numerical receipts independently reconstruct raw-image predictions, masks, margins, class counts, and aggregate summaries. Their evidence is adequate for the R4 numerical claims. I found no concrete discrepancy warranting another numerical rerun. The same images reused across seeds are explicitly accounted for in the manuscript's descriptive statistical treatment.

## Prioritized issue register

| ID | Classification | Exact location and evidence | Required action before review handoff |
|---|---|---|---|
| SCI-01 | Blocking scientific error | No contradiction found in the reviewed proofs, empirical definitions, or claim-to-evidence chain. | None identified. |
| POS-01 | Journal significance judgment — material | Main full-width certificate: zero coverage in every competitive set; original positive coverage concentrated at s_C/16; dense frontiers remain below competitive widths. | Retain the theory-and-diagnosis framing already used in the abstract and conclusion. No claim expansion or additional training is required for this handoff. |
| POS-02 | Journal significance judgment — material | Local bands provide positive coverage; Table “Local-band certification and fitted accuracy” reports all-query accuracies of 11.77–45.06% at the displayed endpoints. Stronger informed selection wins or ties the certificate. | Retain local coverage as a persistence result and preserve the complete selector comparisons. The existing text does so. |
| POS-03 | Journal significance judgment — material | At t=s_C, unique limiting exclusions beyond the expanded bank are 0% on MNIST and 0.134% on Fashion-MNIST; fixed replay measures retrospective recovery. | Retain the demonstrated analytical exclusion capability and the exact sampling-dependent incremental counts. The existing text does so. |
| ED-01 | Optional editorial compression | Abstract and Introduction's final paragraph enumerate many secondary diagnostics; Results has thirteen subsections in the 41-page package. | A later venue-focused edit could move detailed budget-stability and replay summaries to the supplement while preserving the primary negative findings. This is not a validity correction or handoff prerequisite. |

Passages to retain are the opening problem and contribution paragraph, the exact model assumptions, the distinction between certificate failure and strict exclusion, the finite-path definitions, the validation-only selection rule, the class-specific explanation of the MNIST endpoint, and the conclusion's statement of a continuous persistence analysis. They carry the argument and its evidence directly.

## Significance judgment and action

**The scientific contribution is supported. The Neural Networks significance judgment is BORDERLINE.** The paper supplies explicit sufficient and exclusion conditions for a conventional RBF family's decision relation, proves their continuous scope, and evaluates their reach systematically. The most convincing result is the combined characterization of guaranteed persistence, demonstrated incompatibility, and unresolved cases. The R4 extension improves scientific interpretation by exposing zero competitive coverage, nonmonotone finite paths, and class concentration.

The demonstrated reach is concentrated in analytical characterization. The full-width construction accepts the near-isolated-prototype regime; the local-tail construction obtains broader-width guarantees in heavily regularized, low-accuracy models; expanded finite checks reproduce most limiting exclusions at the principal endpoint. These concrete findings make theoretical value the appropriate basis for a journal decision. More numerical reconstruction of the same archive would increase verification volume without changing those findings.

**Recommended next action: hand the frozen R4 package and this review to an independent specialist in RBF or kernel-method theory.** There is no identified scientific repair that must precede that handoff. The assessment of significance is now recorded rather than left as an unanswered placeholder. A later attempt to strengthen the contribution would need a specifically demonstrated new capability, such as informative certification in competitive regimes or a sharper characterization of the unresolved frontier; it is outside the completed saved-evidence plan.

## Review limitations

This review independently checked the mathematical argument and interpreted the supplied experimental evidence. It used the completed independent numerical reconstructions and did not execute new fits or rerun their numerical pipelines. It did not perform a fresh external literature search, independently establish priority over all related work, inspect every PDF page, verify current journal submission instructions, or make a publisher acceptance decision. Those are distinct evidence and production tasks. The configured model and reasoning level are recorded from the explicit successful spawn configuration supplied by the lead agent; backend identity was not separately measured.
