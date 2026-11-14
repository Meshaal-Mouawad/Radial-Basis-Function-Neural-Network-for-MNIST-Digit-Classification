# R4 integrated revision report

14 November 2026 | Neural Networks transfer preparation | Meshaal Mouawad

## Completed manuscript

R4 implements the approved saved-data analyses directly in the LaTeX manuscript. The compiled manuscript has 41 pages, seven figures, twelve tables, and 17 references. The six original figures, mathematical results and approved AI declaration are preserved. No new model was fitted.

## Research changes and locations

| Analysis | Finding integrated | Location |
| --- | --- | --- |
| C: class composition | Class-balanced accuracy, retention, accepted recall, effective class count and exact selected-set overlap. | Sections 5.7, 6.10; Table 9; Figure 7 |
| D: finite paths | Observed first disagreement, sampled return to agreement, sign changes and comparison with sufficient tail bounds. | Sections 5.8, 6.11; Table 10 |
| E: competitive operation | All 30 groups and all 2,880 archived pairs; validation-selected models and 90/95/99% competitive sets. | Sections 5.9, 6.12; Table 11 |
| F: exclusion accumulation | All seven K=100 widths and three floors, using fixed-order original and expanded finite probes. | Sections 5.8, 6.13; Table 12 |
| G: stability | All paired seed results, budget gains, class counts, prediction disagreement and correct-set overlap. | Sections 5.9, 6.12; supplement |

The abstract and introduction state the actual analytical contribution and measured reach. Discussion distinguishes persistence over continuous families, finite-model accuracy, selected-set composition, and observed regularization paths. The single end Limitations section consolidates empirical scope and boundary conditions.

# Verified findings

## Competitive operation and stability

The primary 95%-of-best-validation rule retains 328 models across the 30 groups; every retained model has zero sharp full-width certificate coverage. The 90% and 99% sensitivity sets retain 494 and 116 models with the same zero result. All 30 best-validation models choose zero penalty.

| Dataset | K=50 accuracy (%) | K=100 accuracy (%) | K=200 accuracy (%) |
| --- | --- | --- | --- |
| MNIST | 82.92 ± 0.46 | 88.43 ± 0.27 | 91.80 ± 0.31 |
| Fashion-MNIST | 76.23 ± 0.88 | 79.38 ± 0.63 | 82.13 ± 0.19 |

Accuracy improves at every budget step in every seed. Paired K=50 to K=200 gains are 8.88 ± 0.41 percentage points for MNIST and 5.90 ± 0.80 for Fashion-MNIST. Across the ten seed pairs, prediction disagreement falls from 14.29% to 5.95% and from 12.21% to 8.15%, respectively. Region exclusion is defined separately from endpoint error.

## Finite-path behavior and exclusions

The exhaustive path reconstruction finds 190,405 returns to strict agreement among 3,366,480 query–width paths. Up to five sign changes occur across six sampled penalties. Sufficient tail bounds remain distinct from observed early disagreement and later agreement.

At t=sC and floor zero, the expanded finite archive recovers 95% of the original limiting-witness cases after mean 15.6 checks on MNIST and 20.2 on Fashion-MNIST, in every seed. The original finite archive never reaches that target in the ten groups. These are fixed-order archived-check counts.

## Composition of selected subsets

At the MNIST constant class-1 endpoint, all ten true classes remain represented in the certified subset: selected-class macro accuracy is 10%, despite 68.93% micro accuracy. For Fashion-MNIST at t=sC, gated-distance selection raises selected-class macro accuracy from 25.49% to 44.21% and effective predicted classes from 1.71 to 3.73. The two sets have mean Jaccard 0.313 at equal cardinality.

# Verification and delivery

## Independent numerical reconstruction

| Audit | Verified evidence |
| --- | --- |
| C composition | 20 settings, 40 selector rows, 400 class records, 140,270 prediction labels |
| D/F paths and probes | 20,198,880 labels; 3,366,480 paths; 480 width summaries; 70 bound rows; 1,161 finite masks; 21,630 cumulative rows; 420 region summaries |
| E/G competitive models | 14.4 million validation labels; 20,198,880 evaluation labels; 2,880 independently computed masks; 630 original masks; all summary tables |
| Source/PDF protection | Original protected bytes and math exact; R3 checkpoint unchanged; 41 pages inspected; no layout or cross-reference warnings |

The numerical verifier implements sharp certificates directly from the equations and replays raw images with archived weights. It does not import the production runners or the frozen certificate implementation. The separate source/evidence review and clean-extraction receipts are retained in revision_record/.

## Package and reproducibility

journal_files/ contains the compiled PDF, standalone LaTeX ZIP, complete numerical supplement, revised draft cover letter, highlights, title page and competing-interest files. revision_record/ contains this report, the one-page decision summary, source diff, scientific reviews, build and fresh-extraction checks. preserved_R3/ retains the preceding PDF and source ZIP.

The supplement preserves the complete original R2 evidence and R3 analyses, then adds the adopted plan, composition records, R4 protocols, full arrays, CSVs, plots and four independent verifiers. Its README documents hash verification and fresh reconstruction. The source ZIP compiles independently. Every archive is checked against a SHA-256 manifest.

## Readiness and editorial decision

Internal review readiness is determined by completed analyses, preservation, independent reconstruction, compilation, page inspection and clean-extraction checks. REVIEW_READY.json records those gates and final hashes after all checks pass. This is an internal manuscript version. The Neural Networks transfer/submission process remains incomplete.

## Limitations and significance

The requested analyses are complete. They establish zero competitive full-width coverage, observed nonmonotone paths and exact composition/overlap behavior in the archived model families. Predictive or model-selection benefit and measured computational speedup are not established. The editor’s broader significance judgment remains unresolved. Current portal-specific requirements require checking during submission; no journal submission was performed.
