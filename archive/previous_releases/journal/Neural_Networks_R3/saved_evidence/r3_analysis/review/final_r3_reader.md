# Final independent R3 source and evidence-alignment review

14 November 2026. Reviewed the integrated source in `working_R3/source/`, the M1/M2 and M3 reports, their machine-readable summaries and independent-verification records. No manuscript files were edited by this reviewer.

## Decision

**PASS — integrated source, argument, numerical table alignment and protected-content preservation.** The manuscript now contains the requested threshold, exclusion-overlap and matched-coverage analyses directly in its LaTeX source. Two narrowly defined wording findings were corrected by the lead and re-read in the source. No further material source changes are requested by this review.

The paper claims an analysis of continuous decision persistence. The new results identify the reach of its sufficient reversal bounds and the dependence of empirical exclusion increments on the finite comparator grid. The selected-query comparisons accurately report enrichment over ordinary baselines and the higher accuracy of an agreement-gated distance baseline in three conditions. These findings do not establish a general accuracy advantage or close the editor's significance concern. This remains a separate scientific assessment in the revision record.

## Checks and evidence

| Check | Finding | Result |
|---|---|---|
| Thesis and reader progression | Abstract states the analytical claim first. Introduction explains prototypes, Gaussian width, fitted readouts, the requested parameter family and the three analytical outputs before detailed notation. | PASS |
| R3 method integration | `r3_methods.tex` is included within Evaluation Design; it defines all three follow-up diagnostics and their shared groups. | PASS |
| Validation-reference provenance | `main.tex` now explicitly limits the unused-validation statement to the frozen study. `r3_methods.tex` explains the subsequent 5,000-row-per-seed validation scoring of 96 archived readouts and 95% within-group rule. | PASS |
| Sufficient reversal semantics | The formula minimizes the proven sufficient bound over guarded strict competitors. Results name it a sufficient bound and compare it with the same-width competitive maximum on a common Gram-norm axis. | PASS |
| Missing competitive references | Results explicitly state that no original upper width below `s_C/2` qualifies. The abstract now restricts the all-bounds statement to widths with competitive sampled models. | PASS |
| Exact witness overlap | `L0`, `L+`, `F0` and `F1` have distinct definitions. The original R2 partition remains tied to `L0 ∪ F0`; new comparisons explicitly use the expanded archive. | PASS |
| M2 empirical claim | The text gives original-limit unique contributions of 8.026%/21.458% over original finite probes at `t=s_C`, then 0%/0.134% over all archived finite readouts. It identifies 0.148% as the dense-limit variant. These agree with the report and CSV. | PASS |
| Random comparator | Exact fixed-cardinality expectation is derived by inclusion probabilities and linearity; no Monte Carlo result is invented. | PASS |
| Informed selectors | Ordinary and agreement-gated score/distance rankings are defined with identical within-seed cardinality, label-free ranking and deterministic ties. Raw versus normalized score ranking is distinguished. | PASS |
| Class composition | The text reports the constant class-1 MNIST endpoint, exact 474/4,027 full-query reference, equality of certificate and endpoint-agreement pools, and Fashion-MNIST class frequencies. These match the analysis records. | PASS |
| Abstract and conclusion | Both retain the continuous-region contribution and summarize the actual evidence. Neither claims improved general classification or a validated model-selection benefit. | PASS |
| Limitations placement | Scope, finite-grid support, post hoc design, floating-point status and unresolved predictive/model-selection utility appear together in the dedicated Limitations section. | PASS |
| Appendix references | Both source occurrences now use the class-generated reference directly and no longer prepend an extra “Appendix.” | PASS at source level |

## Direct numerical table comparison

The reviewer checked the displayed rounded values against the actual CSV summaries, independently of the prose reports:

- Every displayed selector accuracy mean and sample standard deviation in `r3_selector_table.tex` was found at the matching rounding in `m3/results/summary.csv`.
- Every displayed median and 90th-percentile threshold in `r3_threshold_table.tex` matches `m1_m2/results/m1_summary.csv` for the six conditions with competitive references.
- Every displayed original-finite, expanded-finite, dense-limit-only-over-original and dense-limit-only-over-expanded mean/SD cell in `r3_overlap_table.tex` matches `m1_m2/results/m2_summary.csv`.

The independent M1/M2 verification record reports 1,260 mask/count comparisons, recovery of all 210 R2 region counts and 338 direct-solve threshold checks, with status PASS. The M3 independent record reports 20 settings reconstructed, 140 selector rows and 1,400 class-count rows verified, zero maximum weight/score discrepancies in that runtime, and unchanged inputs. These records were read; this reviewer did not independently rerun their numerical scripts.

## Protected-content comparison performed in this pass

The following were compared byte for byte between `baseline_source/` and `working_R3/source/`, with equality in every case:

- `results.tex` and `frontier_results.tex`.
- `ridge_theory.tex` and `exact_ridge_examples.tex`.
- `references.bib`.
- All six figure PDFs, including the approved Figure 6.

The original `main.tex` mathematical environments were extracted and compared in sequence. All 17 numbered equation environments, one theorem, two lemmas, two propositions and five proof environments remain exactly equal. The approved AI declaration remains exact. The additional R2 theorem/proposition/proofs are protected by the exact `ridge_theory.tex` equality.

## Findings closed during this review

1. **Overbroad abstract denominator.** The initial draft said every computed finite bound exceeded a competitive reference, although four original widths have no qualifying reference. The lead replaced it with: “At widths with competitive sampled models, every finite sufficient reversal bound exceeds the largest qualifying penalty at the same width.” Re-read and closed.
2. **Ambiguous endpoint label.** The initial Discussion called the constant MNIST model the “full-width endpoint.” The lead replaced it with the explicit condition `t=s_C` and `lambda=10 norm(A_t)_2`. Re-read and closed.

## Final interpretation

The revisions answer the three specified empirical questions. At the widths with competitive validation models, the sufficient bounds lie above all qualifying sampled penalties. Strengthening the finite witness archive removes nearly all unique limiting exclusions at `t=s_C`; the residual varies with the sampled width/penalty support. Certified subsets outperform random and ordinary margin selection in the reported means; agreement-gated distance selection is higher in three conditions and identical in the fourth. These outcomes are stated directly and the continuous guarantee remains the certificate-specific analytical result.

The lead can close the requested source-integration and analysis tasks after final PDF and archive verification. Scientific significance should remain recorded as unresolved rather than inferred from production success.

## Review boundaries

This pass reviewed source, numerical summaries and verification records and performed the preservation and table comparisons described above. It did not inspect every final PDF page or verify the packaged archive. The build log observed during review reported a 36-page PDF; final production counts belong to the lead's post-layout check. Current Neural Networks anonymity and upload requirements remain unverified because its official guide returned 403 in the preceding venue pass.
