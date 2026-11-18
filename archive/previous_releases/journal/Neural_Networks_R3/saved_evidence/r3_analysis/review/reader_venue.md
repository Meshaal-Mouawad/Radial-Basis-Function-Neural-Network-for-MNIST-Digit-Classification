# R3 independent reader and venue review

14 November 2026. Read-only review of the authoritative R2 LaTeX source and prior review records. Target: **Neural Networks**. Author reports transfer selection; the transfer/revision process is not complete. This report does not change manuscript files.

## Decision

The R2 proofs support a coherent analysis of nearest-prototype label persistence over bandwidth–penalty families. R3 should measure the empirical reach and incremental information of that analysis through M1, M2 and M3. The original results, six figures, theorem/proof blocks, references and approved declaration should remain protected. No new generalization, predictive improvement, model-selection benefit or speedup claim is established merely by adding these comparisons.

The editor stated limited significance and asked for evidence of impact. The letter supplied no specific mathematical criticism. R3 should describe the additional measured capability precisely; the revision report should distinguish completion of the requested analyses from resolution of the significance concern.

## Material findings and exact integration actions

| ID | Source and evidence | Finding | Action | Severity |
|---|---|---|---|---|
| R1 | `main.tex:336`: validation partitions are unused; `main.tex:364` and `frontier_results.tex` define the reference as the highest observed accuracy over 16 previously probed widths | The existing 0/1/100 regularization reference uses evaluation labels and is descriptive. It is not a validation-selected competitive range. | If M1 computes new validation scores, identify that as a new post hoc analysis and revise the earlier global statement that validation remains unused. Otherwise call the comparison a sampled descriptive accuracy range. Preserve the frozen-study statement as historical, not as a claim covering new analyses. | MAJOR |
| R2 | `ridge_theory.tex`, Proposition “Large-penalty decision and exclusion” | The displayed threshold is a sufficient bound guaranteeing strict competing victory for every larger penalty. It is not the first actual change of winner. | Name the measured quantity “sufficient reversal threshold” or “bound-guaranteed threshold.” State the strict inequality. Report its normalization by the Gram norm at the same width. Record empirical crossings separately if computed. | MAJOR |
| R3 | `new_results.tex:3`: endpoint limit witness plus narrower-width and archived finite witnesses; shared-chat arithmetic compared only an endpoint zero-penalty fit | A set-difference lower bound against one fitted endpoint does not quantify extra information beyond the entire archived finite grid. | Replace the proposed approximate lower-bound narrative with exact mask intersections/unions from M2. Name all comparator grids, use identical query/region denominators, and distinguish original-grid from expanded-grid results. Keep R2 Figure 6/Table 4 explicitly tied to their original witness set. | MAJOR |
| R4 | `new_results.tex:63`: selective accuracies 69.09/75.27 and 68.93/64.65; `new_methods.tex:13` gives endpoint models | Random matched-size expected accuracy equals full-set accuracy exactly. Enrichment over random selection alone does not establish added value over informed ranking. | Include the exact expectation derivation in new methods, then report fixed-cardinality score-margin, nearest-distance-margin and agreement-gated score-margin comparisons from M3. Use label-free ranking and deterministic ties. Report paired differences and class composition. | MAJOR |
| R5 | `main.tex:378,411`; `elsarticle.cls:1354` defines `\\thesection` as `\\appendixname~\\@Alph\\c@section` | `Appendix~\\ref{app:exact-ridge-examples}` compiles as “Appendix Appendix C.” | In both occurrences, use `\\ref{app:exact-ridge-examples}` alone. Recompile and verify rendered text. | PRODUCTION |
| R6 | Abstract, Introduction final paragraph, Discussion and Conclusion | These sections currently describe the R2 analytical objects accurately. Their final empirical summary must match the new comparisons. | Integrate one concise statement of the new evidence in the abstract and contribution paragraph; interpret M1/M2/M3 in Discussion; retain only supported consequential findings in Conclusion. Avoid duplicating whole results paragraphs. | MAJOR |
| R7 | Prior `GOLD_FINAL_ACCEPTANCE_GATES.md` says scientific gates pass and only administration remains | That verdict predates the current unresolved significance questions. | Preserve it as a dated R2 historical record, and issue a clearly superseding R3 assessment based on new evidence. Do not copy its blanket readiness status into the R3 README or cover letter. | MAJOR |

## Argument and reader map

**Problem:** A nearest training prototype supplies a simple label summary, whereas the learned RBF readout combines the complete labeled sample and can choose a different label.

**Gap addressed:** The fixed conventional ridge RBF family needs computable training-based sufficient and exclusion tests over joint bandwidth–penalty regions.

**Response:** Preserve the residual decomposition, spectral floor and exact majorant envelope; retain the limiting-vote finite exclusion proposition and signed local-band theorem.

**Evidence:** The frozen two-dataset study and R2 diagnostics establish the existing coverage, exclusions and local certificates. R3 tests threshold relevance, incremental exclusions and selected-set accuracy against informed selectors on the same declared groups.

**Contribution supported before new numbers:** A reproducible analysis that can certify complete query–region pairs, exhibit a finite disagreement within others and leave the remainder unresolved. Numerical checks establish implementation agreement with the mathematical construction. The new comparisons determine the measured reach of this contribution.

## Targeted prose guidance for the lead editor

The introduction already explains prototypes, Gaussian width, ridge coefficients and the joint parameter region before presenting formal notation. Retain this progression. The statement of the practical question is intelligible to a first-time specialist. The Related Work section distinguishes the present varied objects from input robustness, label changes and fixed-design parameter paths; preserve that distinction without adding another literature inventory.

Use one added methods subsection for all three R3 comparisons. It should define the competitive reference rule, strict threshold semantics, finite-witness grids and per-seed matched cardinality. The results should answer those questions in the same order. This avoids distributing repeated qualification paragraphs throughout the paper.

For the random selector, let each query's fixed correctness indicator be `G_i` and select exactly `m>0` of the `N` queries uniformly without replacement, independently of correctness. Each inclusion probability is `m/N`; linearity gives expected selected accuracy `N^{-1} sum_i G_i`. Apply the calculation separately within each seed, then summarize the seed outcomes. No Monte Carlo experiment is needed for this expectation. If a certified set is empty, its accuracy is undefined; do not substitute zero.

For class composition, distinguish the majority class of the full evaluation labels, the fitted predicted-class frequencies, and the true-label distribution inside each selected subset. A constant full-set predictor's accuracy is the frequency of its chosen class. A selected subset can exhibit higher accuracy because it concentrates that class. Report the observed pattern directly if M3 confirms it. This is an interpretation of measured composition, not an unmeasured causal explanation.

Use the dedicated Limitations section for the scope of the empirical sample, post hoc analyses, shared evaluation images, finite grids, floating-point guards and remaining lack of demonstrated utility. Definitions needed to interpret an equation or denominator belong beside that equation or result; they are part of the method, not defensive caveats.

The abstract currently repeats the central analytical claim, methods and major results in one coherent paragraph. A more concise R3 abstract can retain the three mathematical constructions and only the central empirical diagnosis plus one new quantitative result. It need not enumerate every comparison. The title remains faithful to the research object and does not need a new name.

## Protected content

- Original `results.tex` and `frontier_results.tex` numerical content and all six approved figure files.
- All R2 theorem/proof and exact-example mathematical content, including strict inequality and tie semantics.
- The existing 17-reference bibliography unless a specific supported correction is necessary.
- The exact approved generative-AI declaration, author metadata and original research artifacts.
- The original near-isolated-prototype interpretation and derived `2.96 × 10^-32` response reported in Discussion.

Retain the identified manuscript and separate title page. Current anonymity requirements have not been recovered from an accessible official journal-specific guide.

## Official venue verification performed 14 November 2026

| Item | Result | Source and direct evidence |
|---|---|---|
| Mathematical neural-network analysis within scope | VERIFIED | Elsevier's official journal description includes mathematical analyses and a Mathematical and Computational Analysis section; neural networks must be central. [1] |
| Articles are an available publication form | VERIFIED | Official journal description lists articles, letters and reviews/tutorials. [1] |
| Current Neural Networks Guide for Authors | NOT VERIFIED | Both official guide URLs returned 403 during this review. [2,3] |
| Current anonymity model, abstract limit, manuscript length, mandatory highlights/graphical abstract, journal-specific upload rules | NOT VERIFIED | These require the journal-specific guide. Do not import requirements from a different journal or historical mirrored guide. |
| Publisher-wide source and submission preparation | VERIFIED | Elsevier support says individual journal rules take precedence; it describes PDF plus editable LaTeX source and journal-specific metadata/upload preparation. [4] |
| Publisher-wide filename preparation | VERIFIED | Elsevier support recommends unique filenames, no special characters, common extensions and length no greater than 80 characters. [4] |

Sources actually opened:

1. https://shop.elsevier.com/journals/neural-networks/0893-6080 — retrieved official description, lines 92–96 in tool result `turn2view3` (also `turn1search4`).
2. https://www.sciencedirect.com/journal/neural-networks/publish/guide-for-authors — 403; `turn3view0`.
3. https://www.elsevier.com/journals/neural-networks/0893-6080/guide-for-authors — 403; `turn3view1`.
4. https://www.elsevier.support/publishing/answer/how-do-i-prepare-my-files-for-submission-in-editorial-manager — official support, retrieved `turn2view2` (also `turn1search1`). It expressly defers to journal-specific policies.

The search also returned historical mirrored author packs and a journal-looking submission domain outside the official publisher domain. Neither was used to establish current requirements.

## Closure status

R2 source reader review: PASS for a coherent, adequately defined mathematical object and claim/evidence chain. R3 integration and empirical interpretation: PENDING actual M1/M2/M3 results. Current journal administrative rules: NOT VERIFIED. A final R3 review must inspect the integrated source after the new analyses, confirm every headline number, and distinguish completed production from the still-evaluated significance case.

## Review boundaries

This pass read the source and prior review records and checked the official venue sources above. It did not execute the experiments, reprove every theorem independently, verify new R3 arrays, compile the manuscript or inspect the final rendered PDF. Numerical and production checks remain assigned to the lead and the two analysis agents.
