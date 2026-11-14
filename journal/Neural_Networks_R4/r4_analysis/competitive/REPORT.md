# R4 E/G: competitive operating regions and seed stability

## Decision

**E complete: zero sufficient coverage in every validation-competitive set.** All 30 original groups were included. The 95%-of-best-validation rule retains 328 archived models; every one has zero sharp full-width certificate coverage. The fixed 90% and 99% sensitivity rules retain 494 and 116 models and also yield zero coverage. This closes the specified practical-model-selection question for the archived grid.

**G complete: accuracy and prediction stability improve with prototype budget in these archived models.** Validation-selected evaluation accuracy increases at each budget step in every seed of both datasets. The full-width certificate remains empty. The parameter-region exclusion rate is reported separately from pointwise disagreement and true-label error.

## Selection and reconstruction

Each of the 30 groups has 20,000 training rows, 5,000 validation rows, 16 original widths, and six original penalties. Every archived readout was scored on its validation rows; these rows are disjoint from training and, for MNIST, from the 4,027 reserved evaluation rows. Fashion-MNIST uses its separate 10,000-row test set. Maximum validation correct count selects one model; ties resolve by smaller numerical width and then smaller penalty. The same group-best validation count defines the 90/95/99% retained sets. All 30 selected models use zero penalty; widths vary from 0.75 to 2 times s_C.

Evaluation targets are indexed after validation selections are fixed. Existing evaluation predictions are scored once, with no use of their accuracy to choose a model. The surface records all archived pairs and masks, so there is no favorable-seed omission. The original query feature normalization and strict guards are retained.

The sharp certificate is recomputed at each actual probe pair (sigma,lambda), covering (0,sigma] × [lambda,infinity). Limiting-vote witnesses use all original probe widths up to sigma. Finite exclusions use original probe widths up to sigma and original penalties at least lambda, with full numerical rank required at zero penalty. Their union excludes the requested region for a query. These witnesses can occur at another point in that region; they are not errors of the endpoint classifier.

## Validation-selected models

Values are five-seed mean ± sample SD. Evaluation accuracy, nearest-prototype agreement, certificate coverage and region exclusion have the full evaluation population as denominator.

| Dataset | K | Validation accuracy (%) | Evaluation accuracy (%) | Nearest agreement (%) | Certificate coverage (%) | Region excluded (%) |
|---|---:|---:|---:|---:|---:|---:|
| MNIST | 50 | 82.52 ± 0.71 | 82.92 ± 0.46 | 65.75 ± 5.37 | 0.00 ± 0.00 | 87.53 ± 0.28 |
| MNIST | 100 | 87.64 ± 0.63 | 88.43 ± 0.27 | 73.94 ± 2.43 | 0.00 ± 0.00 | 88.07 ± 0.14 |
| MNIST | 200 | 91.23 ± 0.35 | 91.80 ± 0.31 | 79.83 ± 2.52 | 0.00 ± 0.00 | 88.24 ± 0.14 |
| Fashion-MNIST | 50 | 76.70 ± 0.48 | 76.23 ± 0.88 | 62.72 ± 4.74 | 0.00 ± 0.00 | 98.23 ± 3.13 |
| Fashion-MNIST | 100 | 79.76 ± 0.62 | 79.38 ± 0.63 | 68.35 ± 4.02 | 0.00 ± 0.00 | 93.75 ± 8.61 |
| Fashion-MNIST | 200 | 82.77 ± 0.53 | 82.13 ± 0.19 | 73.58 ± 1.69 | 0.00 ± 0.00 | 77.30 ± 4.81 |

## Fixed validation thresholds

| Dataset | K | Models at 90% | Models at 95% | Models at 99% | Nonzero certificate coverage |
|---|---:|---:|---:|---:|---:|
| MNIST | 50 | 74 | 57 | 28 | 0 |
| MNIST | 100 | 81 | 60 | 17 | 0 |
| MNIST | 200 | 87 | 54 | 14 | 0 |
| Fashion-MNIST | 50 | 79 | 49 | 17 | 0 |
| Fashion-MNIST | 100 | 84 | 56 | 21 | 0 |
| Fashion-MNIST | 200 | 89 | 52 | 19 | 0 |

Counts pool the five seed models within each dataset/budget (480 candidates). They do not count independent evaluation samples. All per-seed retained counts, zero-coverage cases, accuracy/agreement/exclusion ranges and masks are preserved.

## Paired budget differences

| Dataset | Budget step | Evaluation accuracy difference (pp) | Positive seeds | Correct-set Jaccard |
|---|---:|---:|---:|---:|
| MNIST | 50 → 100 | 5.51 ± 0.60 | 5/5 | 0.896 ± 0.008 |
| MNIST | 100 → 200 | 3.37 ± 0.35 | 5/5 | 0.940 ± 0.004 |
| MNIST | 50 → 200 | 8.88 ± 0.41 | 5/5 | 0.877 ± 0.004 |
| Fashion-MNIST | 50 → 100 | 3.15 ± 0.83 | 5/5 | 0.903 ± 0.010 |
| Fashion-MNIST | 100 → 200 | 2.75 ± 0.56 | 5/5 | 0.918 ± 0.008 |
| Fashion-MNIST | 50 → 200 | 5.90 ± 0.80 | 5/5 | 0.868 ± 0.005 |

All five paired values are in `budget_paired_per_seed.csv`. The 50→200 differences are 8.88 ± 0.41 percentage points for MNIST and 5.90 ± 0.80 for Fashion-MNIST. This is a comparison of validation-selected archived models at nested prototype budgets.

## Cross-seed overlap

| Dataset | K | Mean prediction disagreement (%) | Mean correctness Jaccard |
|---|---:|---:|---:|
| MNIST | 50 | 14.29 | 0.874 |
| MNIST | 100 | 9.54 | 0.915 |
| MNIST | 200 | 5.95 | 0.947 |
| Fashion-MNIST | 50 | 12.21 | 0.885 |
| Fashion-MNIST | 100 | 9.74 | 0.909 |
| Fashion-MNIST | 200 | 8.15 | 0.922 |

These are descriptive averages over the ten seed pairs per dataset/budget. Every seed uses the same evaluation image IDs: 4,027 unique MNIST images and 10,000 unique Fashion-MNIST images. The number of probes, budgets, or seed pairs is not an independent sample size. Overlap between validation sets is explicitly stored. No hypothesis tests or confidence intervals are asserted. Jaccard is defined as 1 for two empty certificate sets; all validation-selected certificate sets are empty, so that identity supplies no positive-certification evidence.

Class-specific recall, predicted-class share and certified class counts for all 30 selected models are provided in `validation_best_class_counts.csv` (300 class rows).

## Verification and measured cost

- Pilot: MNIST seed 11, K=50, 1.62 seconds.
- Full invocation: 109.66 seconds; total recorded group reconstruction time 109.56 seconds.
- Single-thread numerical work; per-group checkpoints support safe resume.
- 2,880 archived models, 14,400,000 validation labels, and 20,198,880 reconstructed evaluation labels.
- All 630 archived sharp certificate masks (30 × 7 × 3) recovered exactly; no archived prediction mismatch, certified endpoint disagreement or certified/excluded overlap.
- K=100 validation arrays reproduce R3 results exactly.
- No new fitting, paid computation, inference tests, GitHub modifications or journal submission.
- The implementation performs the documented checks; separate independent verification is supplied by the numerical-review agent and must be cited separately.

## Files and reproduction

`results/surface_per_model.csv` contains all 2,880 pairs. Group NPZs contain full validation/evaluation arrays, selections and diagnostic masks. Per-seed, six-row summary, threshold sensitivity, budget-paired, cross-seed and class tables are separate CSVs. `COMPLETE.json` records input/source/protocol hashes and runtime; each group has a checkpoint receipt and the result folder has a SHA-256 manifest.

```bash
python r4_analysis/competitive/run_competitive.py --evidence evidence
python r4_analysis/competitive/make_plots.py
```

Unchanged checkpoints are reused only when protocol, runner, data, source archive and checkpoint hashes match. `--pilot` processes the first group only. `--output` chooses another destination. NumPy, SciPy, threadpoolctl and Matplotlib are required. The original frozen certificate source is loaded from the evidence tree, never edited.

## Figure captions

**competitive_accuracy_coverage.pdf:** Accuracy and full-width certificate coverage across all 2,880 original archived readouts. Panels separate dataset and prototype budget; each has five seeds × 96 readouts. Teal circles identify models whose validation accuracy is at least 95% of their own group’s best validation accuracy. Evaluation accuracy is displayed after validation selection. Every retained model has zero certificate coverage. Points reuse common evaluation images and are descriptive model configurations.

**validation_selected_budget_accuracy.pdf:** Evaluation accuracy of the validation-best archived readout at each prototype budget. Thin lines connect the same seed; thick markers and error bars show five-seed means and sample standard deviations. All selected readouts use zero penalty; bandwidth is chosen from the archived grid using validation labels. Shared evaluation images are retained across seeds and budgets.

Both figures were rendered and visually inspected: labels, legends, points, axes and error bars are readable and unclipped.
