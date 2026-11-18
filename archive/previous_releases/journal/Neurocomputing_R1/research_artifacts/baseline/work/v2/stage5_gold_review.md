# Stage 5 — GOLD Chief Editor review of v2

Review date: 6 November 2026. Author: Meshaal Mouawad. Working manuscript: *Training-Derived Regions of Nearest-Prototype Agreement in Gaussian RBF Classifiers*. Authoritative scientific sources: `work/v2/manuscript/main.tex`, `results.tex` and `references.bib`.

**Final decision: COMPLETE WITH RECORDED VENUE/ADMIN CHECK.** The scientific manuscript, independent Stage 4 review and final 16-page production artifact pass. No unresolved critical or major scientific, writing, source-attribution, numerical-reporting or rendering issue remains. The outstanding items are the recorded current venue requirements, exact open-access agreement participation, and author-only declarations. This is an internal readiness decision; the journal makes its own editorial decision.

## Scientific decision

**G2 PASS.** The v2 work establishes a sufficient, computable condition for a Gaussian ridge RBF classifier to return a query's nearest-prototype label throughout `(0,t] × [lambda0,infinity)`. The condition is derived from fixed labeled training data, selected prototypes and query distances, without fitting output weights. Its proof and completed numerical evidence close the v1 missing-contribution finding.

The scientific genre is a theoretical/methodological article with controlled computational evaluation. Neurocomputing's official scope includes theoretical understanding of neural networks and learning systems. The completed theorem addresses that standard through a new, precisely delimited operation and an explicit account of the conditions under which it applies. The narrow empirical coverage is reported as a finding of the sufficient condition. It does not call for an unrelated state-of-the-art classification objective.

No additional scientific experiment is required by this review. The manuscript already reports the identical sharp/basic masks, zero coverage at the other six bandwidth endpoints, large seed variation on some Fashion-MNIST conditions, and agreement outside certified regions. These findings are retained in the abstract, main Results, figures, Discussion and consolidated Limitations where each occurrence serves a distinct reporting or interpretive function.

## Cold-start identity, authority and protected record

The study asks whether a conventional learned Gaussian RBF readout can receive a reliable nearest-prototype label summary across a complete two-parameter region. Existing prototype work identifies that proximity and learned class output can differ; safe-inference work already establishes bounds over regularization intervals. The present response uses a specific prototype-label reference, a symmetric Gaussian selected-row block, label-specific overlap terms, and a two-endpoint penalty envelope to establish agreement as both width and penalty vary.

The April 10, 2026 report and pinned repository commit `fc7ff848d10b7f060e028b2271fbfc9ce8687798` remain the historical baseline. The v1 study is a preserved earlier experiment. The v2 theorem, frozen protocol and completed run are dated November 6, 2026. This distinction is maintained in the study records; no new result is backdated to April.

The evidence authority is: mathematical definitions and executable operations; frozen inputs, predictions, masks and results; independent reconstruction records; original research papers; manuscript; prior editorial decisions; official venue requirements. The review read the complete GOLD prompt, complete main text and included Results, theory and independent proof review, protocol, production certificate source, completion record, implementation audit, source comparisons, full analysis summary, canonical dataset provenance, final Stage 4 review, production verification and the separate journal/author check records.

Protected objects include the model's sum-of-squares objective, no-intercept rule, fixed selected training prototypes, isotropic shared Gaussian width, residual identity, exact majorant supremum, strict certificate, bound ordering, frozen data splits and hashes, numerical prediction arrays, all declared grid outcomes and source identities. The scientific manuscript preserves these objects.

## Contribution and evidence reconciliation

| Claim | Direct evidence | Accepted interpretation |
|---|---|---|
| Continuous width/penalty agreement region | Main-text residual lemma, spectral lemma, penalty-envelope proposition and agreement theorem; independent proof review | A sufficient parameter-region statement with explicit applicability and strict-margin conditions |
| Exact two-endpoint maximization | Convex-majorization proof and limiting endpoint in the penalty-envelope proposition | Exact supremum of the specified nonnegative majorant |
| Bound hierarchy | Main-text proof of `D_sharp <= D_basic <= D_F`; independent constant and mask checks | Analytical no-worse bound and nested certified query sets |
| Effect of retaining class-specific terms | Matched methods on all 630 regions and immutable mask archives | Larger certified sets than the cancellation-aware Frobenius comparator, with identical sharp/basic sets in the experiment |
| Numerical and empirical behavior | Two separately written synthetic checks; frozen two-dataset run; independent reconstruction of all reported counts | Reproducible implementation evidence and measured coverage under the declared design |
| Preparation cost | Parenthesized `E.T @ (E @ Y_C)` and direct accumulation argument | `O(N K C)` preparation after feature construction, plus class-pair work; the experiment records descriptive timing |

The continuum statement is established by the proof. The finite probes exercise the implementation. Agreement with a prototype label and correctness against the held-out target remain separate outcomes throughout the manuscript.

The previous G2 failure concerned characterization of established width behavior without a new explanatory condition. V2 supplies that condition and measures its actual output. That finding is closed. Predicting every transition outside certified regions, adding learned feature encoders, or adding an accuracy-ranking competition would change the accepted research question and is not a prerequisite for this paper's stated result.

## Closest-work and source gate

The more detailed comparison is `editorial_science_assessment.md`. The final manuscript correctly distinguishes four relevant capabilities: architectural control of prototype-class relationships, analysis of learned sample influence, Gaussian-scale/feature geometry, and safe parameter-range inference. The related-work sequence develops those capabilities before stating the present operation.

The final source repair changes the Softmax paper's authors from an incorrect preliminary attribution to **Mahsa Fazaeli-Javan and Kamaledin Ghiasi-Shirazi**. The publisher's indexed author-contribution statement supports these names. I verified the correction in the Introduction citation key, author-prominent Related Work, comparison table, Discussion and bibliography. The Fashion-MNIST dataset's correct Xiao et al. (2017) reference remains unchanged. The added Ndiaye et al. paragraph correctly acknowledges fixed-design regularization-path guarantees before explaining the simultaneous Gaussian-width/penalty question.

| Source | Verified support used by the paper | Access/source record |
|---|---|---|
| Saralajew et al. (2025), DOI 10.1609/aaai.v39i19.34233 | Unconstrained output weights can separate closest components from class output; probabilistic prototype architecture and input robustness | Author full text, Sections 2–3 and Theorem 1; `editorial_science_assessment.md` |
| Fazaeli-Javan and Ghiasi-Shirazi (2026), DOI 10.1016/j.neucom.2026.133904 | Positive/negative learned prototypes, near-boundary training-sample influence on Softmax neurons | Publisher-indexed abstract, Introduction, section excerpts and authorship statement; exact author correction closed |
| Noorizadegan, Wang and Ling (2026), DOI 10.1016/j.neucom.2026.134771 | First-layer Gaussian-scale geometry and practical scale interval | Author version v3, August 12, 2026; publisher online August 10 record |
| Noorizadegan (2026), DOI 10.1016/j.neucom.2026.135408 | Shepard-normalized Gaussian edge features, constant reproduction and scale-sensitivity evaluation | Author version v2 and publisher online October 14 record |
| Ndiaye et al. (2019), PMLR 97:4771–4780 | Fixed-design safe regions and validation/prediction bounds along regularization intervals | Publisher full PDF, Sections 2–4, Lemma 4, Proposition 7 and Conclusion |
| Voráček and Hein (2022), PMLR 162:22361–22383 | Nearest-prototype robustness to input changes | Publisher abstract and bibliographic record, independently reopened |
| Rosenfeld et al. (2020), PMLR 119:8230–8241 | Prediction certification against changed training labels through randomized smoothing | Publisher abstract and bibliographic record, independently reopened |
| Bindel (2025), Cornell CS 6210 notes | Established residual-based solution-error relation | Primary course notes, residual-bounds section, independently reopened |
| Broomhead and Lowe (1988); Wurzberger and Schwenker (2024) | Linear output estimation in RBF formulations; geometry/initialization in deep RBF learning | Earlier verified primary-source ledger, claims remain within inspected evidence |
| LeCun et al. (1998); Xiao et al. (2017) | Dataset identities | Original references plus creator-distributed data and canonical payload audit |

## Complete-reader and argument review

**G3/G4 PASS.** A specialist unfamiliar with the project can reconstruct the problem, model, requested certificate, mathematical mechanism, experiment and finding from the article alone.

The opening paragraph states the scientific difficulty and response. The following paragraph defines a prototype, Gaussian response, width and ridge output purpose before relying on the formal notation. The mathematical development then follows the actual dependency order: model, self-response/overlap split, residual identity, spectral floor, uniform penalty envelope, query margin and certificate. The comparator derivation explains what information each simplification discards. The duplicate-input appendix provides a compact constructed example that shows why non-prototype training labels matter.

The evaluation questions connect to methods and Results in the same order: coverage, comparator differences, endpoint agreement/accuracy, and numerical verification. Discussion explains the measured coverage through the monotonic directions of overlap, spectral floor and competing-class query mass. Conclusion states the established operation and measured behavior. Extended boundaries are consolidated in the final main-text Limitations section, while assumptions necessary to define a theorem remain with the theorem.

No paragraph-level defect warrants a substantive rewrite. Technical terms and symbols arrive with their purpose, repeated findings serve distinct section functions, and editorial process labels do not appear in the scientific argument. The separately recorded author declarations contain the required factual administrative material for finalization.

## Method and numerical audit

**G6/G7 PASS.** All model assumptions, normalization choices, splits, prototype rules, parameter endpoints, finite probes, tie policy, guard, numerical solver and denominator definitions agree with the frozen implementation.

The primary MNIST reserve contains 4,027 images excluded from every earlier training/validation partition; Fashion-MNIST uses its official 10,000-image test set. Canonical MNIST images and labels are byte-identical to the supplied arrays in the same observation order, as recorded in `design/canonical_dataset_provenance.json`. Evaluation labels were used for scoring after every group's predictions and masks were written and hashed. The full loaded MNIST label array is accurately described; the paper does not claim reserved labels were physically absent from memory.

I independently recomputed central coverage and endpoint summaries from the result CSVs. The separate implementation audit reconstructs all 630 endpoint rows and all 1,890 certificate/accuracy rows from archived arrays. Its source and manifest checks pass. In particular:

- The sharp method certifies 587,703 of 4,418,505 query-region cases; basic has identical masks.
- The Frobenius comparator certifies 285,286 cases and is a subset in every region.
- All positive coverage occurs at `s_C/16`. The other six endpoints retain zero coverage.
- Exactly 102 of 630 regions have an inapplicable zero denominator; they remain in coverage denominators.
- Sharp produces 5,289,327 certified finite-probe comparisons; all methods produce 13,146,228 method-tagged comparisons. Within-group deduplication gives 3,585,477 query/parameter checks. Every checked count has zero disagreements.
- All 480 saved feature factorizations have full numerical column rank; they support 2,880 fitted readouts.
- The smallest certified raw margin is `1.4658047523541384e-05`, and the smallest margin/guard ratio is approximately 51,145.07.
- Mean and sample SD entries include all five seeds, including zero-coverage realizations. Repeated queries and overlapping parameter conditions are described accurately.

The main table's 18 rows reproduce the immutable summaries. The direct endpoint comparison at `K=100`, zero penalty separates nearest-label agreement from class accuracy. The wall-clock value, 123.20 seconds, is a descriptive execution record. The paper does not infer an unmeasured runtime advantage from the arithmetic count.

## Visual content review

I inspected both complete source figure images and final manuscript pages 4, 10, 11 and 12. Figure 1 answers where the certificates cover queries and retains all scaled endpoints and zero-seed outcomes. Figure 2 separates fitted label agreement from readout accuracy and fixed nearest-prototype accuracy. Axes, panel labels, seed markers and color/line distinctions are clear at their final layout size. Both captions define the evaluation population, fixed prototype budget, penalty floors, scale, and mean/individual-seed encoding. The related-work table is placed before the model section on page 4; the complete 18-row numerical table is legible on page 11. Both result figures precede Discussion.

Root inspected all 16 final pages, including the equations and reference list, and recorded PASS in `PRODUCTION_VERIFICATION.json`. I read that record and independently matched all six recorded source, PDF and figure hashes to the actual files. Its final log has no warning, overfull-box or undefined-reference line; all 12 citations resolve; every PDF font is embedded; and both figure PDFs are byte-identical to the analysis exports. The cover letter and separate Highlights Word file have also been rendered and inspected by root.

## Independent review and artifact closure

Stage 4's final decision is PASS and names the same source and PDF hashes as this review. Its material fixes are closed: the Frobenius bound uses the intended `\\eta_t^2` symbol; the reference-weight description states the coefficient structure; the residual proof uses the normal equations for the fitted weights and the definition of the reference residual; the saved minimum margin is accurately called raw; and the 2026 Softmax attribution is corrected. The abstract explicitly identifies mean coverage. The production changes improve table alignment and float placement without altering protected scientific content.

The immutable evidence audit verifies all 71 v2 result files and all 45 preserved prior-study files. The assembled evidence package verification passed before addition of manuscript/review materials. Root performs the final release archive verification after copying these final records; the ZIP checksum and archive manifest belong to that release record. The present decision is tied to the reviewed manuscript and evidence identities below.

| Final scientific artifact | SHA-256 |
|---|---|
| `main.tex` | `316a3ae98549cff890489a6c7888daea6e339fa3e98da5e4ccdf2db4667d017f` |
| `results.tex` | `6d1b2b0907d6cd09331a329da3261b9f5eaf541cd292398fe8400d5dfd38acd1` |
| `references.bib` | `4c87c2ec1cb0e79999b39cb4fdde2c511d3babb72d763b7e584ebdf1e077d03f` |
| `main.pdf` | `a06a48e271c44f063cce74a2609fffe346be6093ec12a3157cec5a93cfc4d251` |
| `figure1_coverage_profiles.pdf` | `20063712cd330ccc63857de74d28c04fe69f9c89c27bc0ab917519e154780b6b` |
| `figure2_agreement_accuracy.pdf` | `938c04f4455457d74dd5c72cf6760a96d214600f3f38ea3b7a4e1ff5cd500c73` |

## Issue register and closure

| Issue | Status | Evidence and action |
|---|---|---|
| v1 lacks an externally meaningful explanatory operation | CLOSED | v2 full-region theorem and completed coverage comparison |
| General no-refitting inference or parameter intervals presented as absent | CLOSED | Ndiaye et al. relationship integrated into Related Work and comparison table |
| Softmax article incorrectly attributed to Xiao et al. | CLOSED | Corrected all 2026 occurrences to Fazaeli-Javan/Ghiasi-Shirazi and `fazaeli2026`; publisher authorship verified |
| Exact supremum could be confused with exact model discrepancy | CLOSED | Proposition and following paragraph identify the selected nonnegative majorant |
| Sharper bound could be presented as empirically superior to basic | CLOSED | Abstract, Results and Discussion explicitly retain identical masks and zero observed extra certification |
| Zero coverage or zero seeds could be omitted | CLOSED | Main table, figure, complete Results and full archive preserve them |
| Numerical grid could be mistaken for a continuum proof | CLOSED | Theorem proof and finite-check purpose stated separately |
| Duplicate inputs could invalidate an unrestricted small-width statement | CLOSED | Appendix states the correct separation assumption and gives the contradictory-label example |
| Current journal-specific formatting and exact APC title eligibility | OPEN ADMINISTRATIVE | Named in `submission/JOURNAL_AND_AUTHOR_CHECKS.md` |
| Author-only contact, funding, conflicts, contributions, approval and publisher disclosures | OPEN AUTHOR FINALIZATION | Factual drafts and unknowns identified in `submission/AUTHOR_DECLARATIONS_TO_FINALIZE.md` |
| Stage 4 notation, reference-weight explanation, residual-proof premise and raw-margin description | CLOSED | Corrected source, independent Stage 4 PASS and final artifact identity checks |
| Final rendered manuscript and Stage 4 closure | CLOSED | Final 16-page production PASS; direct final figure/table inspection; six hashes independently matched |

## Final gate register

| Gate | Status | Evidence/disposition |
|---|---|---|
| G1 Venue | NOT VERIFIED in full | Scientific fit PASS; current author-guide specifics and exact agreement title participation remain recorded administrative checks |
| G2 Contribution | PASS | New finite-region operation, verified proof, measured coverage and closest-work comparison |
| G3 Reader | PASS | Complete cold-reader sequence and definitions checked |
| G4 Continuity | PASS | Question, theorem, evaluation, Results and interpretation align |
| G5 Sources | PASS | Corrected author attribution, claims within inspected evidence and all 12 compiled citations resolved |
| G6 Methods | PASS | Frozen protocol/source and independent implementation audit |
| G7 Results | PASS | Complete negative findings and all numerical counts independently reconstructed |
| G8 Figures | PASS | Source figures and final pages 4, 10, 11 and 12 inspected; captions, labels and numerical table readable |
| G9 Preservation | PASS | Frozen v2 source/input/results match manifests; all prior-study files preserved; final manuscript identities recorded |
| G10 Production | PASS for reviewed manuscript and submission materials | Final 16-page compilation and whole-document visual inspection pass; reference resolution, embedded fonts and matching figure identities verified; release archive verification is recorded separately by root |
| G11 Authorial voice | PASS | Unified scientific article, process materials kept in separate records |
| G12 Closure | PASS | Material scientific and writing issues closed; independent Stage 4 PASS and final manuscript production PASS; remaining author/venue items are explicitly recorded |

## Retain decisions

Retain the current article structure, developed model explanation, exact proofs, explicit majorant wording, complete grid reporting, conservative/no-improvement findings, distinct class-accuracy measurements, duplicate appendix, and consolidated Limitations. The supported scientific argument requires no additional expansion. Final changes should address a verified source, rendering, package or venue requirement.

## Remaining author and venue actions

The current official journal guide was inaccessible, so the final submission portal must supply its abstract/length/anonymization and upload-category rules. Mississippi State University's agreement is verified at publisher/institution level; Neurocomputing title participation and allocation at acceptance remain to be confirmed. The author must finalize correspondence details, affiliations and author list, funding/conflicts/CRediT, approval and exclusive-submission assertions, and the publisher's required writing/research tool-use disclosures. The records supply factual drafts and do not assert that the author has already reviewed the delivered manuscript.

These are the remaining venue and author-finalization items supporting the final category **COMPLETE WITH RECORDED VENUE/ADMIN CHECK**. The scientific article and its reviewed production files are complete. The separate release verification must accompany the delivered archive.
