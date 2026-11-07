# Supplementary post hoc bandwidth frontiers (M1)

The analysis brackets each query’s largest accepted guarded-certificate width and measures the fitted readout at widths selected from coverage alone. All 30 frozen dataset/seed/prototype groups and all three ridge floors are retained.

## Protocol and audit

- The final protocol and runner were hashed before execution in `FREEZE.json`. The 67-point geometric grid spans $s_C/32$ through $s_C/4$, with 22 intervals per doubling. Adjacent widths differ by $2^{1/22}=1.03200828$; each uncensored transition has a multiplicative bracket no wider than 3.21%.
- The original `certificate.py` was imported unchanged, with its strict gap/tie guards. Every query/floor/method has a stored last passing index, next failing index, masks and left/right censor flags. Analytical monotonicity permits these brackets; every observed mask nesting relation was checked.
- The largest sharp-certified width with any coverage, with at least 50% coverage, and with at least 90% coverage was selected independently for each group/floor. Choices used no evaluation targets. Each selected width was fitted using the archived thin-SVD ridge reference. All prediction archives were hashed before the separate evaluation-label files were scored.
- The shared original widths $s_C/16$, $s_C/8$ and $s_C/4$ reproduce the frozen masks exactly. Method subset relations and numerical nesting pass. Every certified endpoint prediction agrees with the nearest-prototype label.
- The first attempt stopped in the first group because a 65-point grid did not contain the two interior shared widths. Its source, protocol, freeze, environment and failure log are preserved in `attempt_01_aborted`. The corrected 67-point protocol was refrozen before any completed group archive or scoring.
- Completed local runtime: 172.3 seconds. All 18,090 group/width/floor/method coverage rows and 270 selected endpoint rows are archived.

## Measured operating frontiers

Entries below summarize the 15 groups per dataset (five seeds and three prototype budgets). Width and coverage ranges concern the largest grid width retaining at least one sharp-certified query. Accuracy, agreement and loss are arithmetic means across the 15 paired group outcomes.

| Dataset | Floor | Frontier $t/s_C$ range | Coverage at frontier range | Readout accuracy | Nearest agreement | Loss vs best frozen sampled accuracy |
|---|---:|---:|---:|---:|---:|---:|
| mnist | 0 | 0.07792–0.11020 | 83.16–94.93% | 69.85% | 99.68% | 17.96 pp |
| mnist | 1 | 0.07792–0.11020 | 74.17–95.95% | 69.85% | 99.67% | 17.42 pp |
| mnist | 100 | 0.08042–0.11020 | 85.30–95.13% | 69.85% | 99.67% | 9.09 pp |
| fashion_mnist | 0 | 0.04021–0.11737 | 42.77–94.69% | 62.97% | 99.53% | 16.32 pp |
| fashion_mnist | 1 | 0.05013–0.11737 | 36.62–92.01% | 62.98% | 99.45% | 15.16 pp |
| fashion_mnist | 100 | 0.09414–0.11737 | 45.72–92.33% | 63.02% | 99.26% | 8.04 pp |

The largest accepted grid ratio across all groups and floors is 0.11737; its Gaussian overlap at the median prototype distance is exp(−1/0.11737²) = 2.96e-32. The denser grid therefore locates the certification boundary within a regime where fitted labels remain almost identical to nearest-prototype labels. At these measured endpoints, broader sampled widths improve true-class accuracy by the paired losses reported above.

The $K=100$ groups used for the main figure have the following paired means and frontier ranges:

| Dataset | Floor | Frontier $t/s_C$ mean (range) | Readout accuracy | Best frozen sampled accuracy | Paired accuracy loss |
|---|---:|---:|---:|---:|---:|
| mnist | 0 | 0.09323 (0.08565–0.10678) | 70.55% | 88.45% | 17.90 pp |
| mnist | 1 | 0.09378 (0.08839–0.10678) | 70.55% | 87.97% | 17.42 pp |
| mnist | 100 | 0.09378 (0.08839–0.10678) | 70.55% | 79.64% | 9.09 pp |
| fashion_mnist | 0 | 0.08370 (0.04021–0.10678) | 63.32% | 79.42% | 16.10 pp |
| fashion_mnist | 1 | 0.08985 (0.05013–0.10678) | 63.33% | 78.23% | 14.90 pp |
| fashion_mnist | 100 | 0.10227 (0.09715–0.10678) | 63.37% | 71.39% | 8.03 pp |

The comparison reference is the largest observed accuracy among the 16 frozen probe widths at the same ridge penalty, evaluated on the same queries. It is a descriptive post hoc sampled reference. No evaluation labels enter supplementary frontier or endpoint-width selection.

## Coverage targets

| Dataset | Floor | Target | Available groups / 15 | Mean selected $t/s_C$ | Mean actual coverage | Mean readout accuracy | Mean loss vs frozen reference |
|---|---:|---|---:|---:|---:|---:|---:|
| mnist | 0 | 50pct | 15/15 | 0.09299 | 90.86% | 69.85% | 17.96 pp |
| mnist | 0 | 90pct | 15/15 | 0.09178 | 94.66% | 69.85% | 17.96 pp |
| mnist | 1 | 50pct | 15/15 | 0.09335 | 89.69% | 69.85% | 17.42 pp |
| mnist | 1 | 90pct | 15/15 | 0.09254 | 93.73% | 69.85% | 17.42 pp |
| mnist | 100 | 50pct | 15/15 | 0.09352 | 91.37% | 69.85% | 9.09 pp |
| mnist | 100 | 90pct | 15/15 | 0.09254 | 94.62% | 69.85% | 9.09 pp |
| fashion_mnist | 0 | 50pct | 15/15 | 0.08809 | 84.76% | 62.97% | 16.33 pp |
| fashion_mnist | 0 | 90pct | 15/15 | 0.08587 | 93.60% | 62.97% | 16.33 pp |
| fashion_mnist | 1 | 50pct | 15/15 | 0.09317 | 76.82% | 62.99% | 15.16 pp |
| fashion_mnist | 1 | 90pct | 15/15 | 0.08929 | 93.28% | 62.98% | 15.16 pp |
| fashion_mnist | 100 | 50pct | 15/15 | 0.10212 | 74.50% | 63.01% | 8.05 pp |
| fashion_mnist | 100 | 90pct | 15/15 | 0.09520 | 93.85% | 62.99% | 8.07 pp |

## Censoring and zeros

| Dataset | Floor | Method | Left-censored query/group records | Right-censored query/group records |
|---|---:|---|---:|---:|
| mnist | 0 | sharp | 2 | 0 |
| mnist | 0 | basic | 2 | 0 |
| mnist | 0 | cancellation_frobenius | 2 | 0 |
| mnist | 1 | sharp | 2 | 0 |
| mnist | 1 | basic | 2 | 0 |
| mnist | 1 | cancellation_frobenius | 2 | 0 |
| mnist | 100 | sharp | 2 | 0 |
| mnist | 100 | basic | 2 | 0 |
| mnist | 100 | cancellation_frobenius | 2 | 0 |
| fashion_mnist | 0 | sharp | 124 | 0 |
| fashion_mnist | 0 | basic | 124 | 0 |
| fashion_mnist | 0 | cancellation_frobenius | 50,009 | 0 |
| fashion_mnist | 1 | sharp | 108 | 0 |
| fashion_mnist | 1 | basic | 108 | 0 |
| fashion_mnist | 1 | cancellation_frobenius | 50,009 | 0 |
| fashion_mnist | 100 | sharp | 95 | 0 |
| fashion_mnist | 100 | basic | 95 | 0 |
| fashion_mnist | 100 | cancellation_frobenius | 50,009 | 0 |

Counts are repeated query/group records; seeds and prototype budgets share evaluation images. Left censor means no grid width was accepted, so no positive frontier is assigned. Right censor means the frontier extends beyond the largest grid width. Complete zero coverage remains in `grid_coverage.csv`.

## Evidence files

- `results/grid_coverage.csv`: every dense-grid coverage result.
- `results/endpoint_metrics.csv`: all selected endpoint metrics, missing targets and paired frozen-reference losses.
- `results/endpoint_summary_by_dataset_K_floor.csv`: dataset/budget/floor/target summaries.
- `results/query_frontier_summary.csv`: group frontier summaries and censor counts.
- `results/<group>/frontiers_before_labels.npz`: per-query masks/brackets, indices, constants, endpoint predictions and weights.
- `results/<group>/PREDICTIONS_FROZEN.json` and `results/ALL_PREDICTIONS_FROZEN.json`: chronology and hashes.
- `results/training_diagnostics.csv`, `results/environment.json`, `results/progress.csv`, `results/MANIFEST_SHA256.json`: diagnostics and provenance.

## Sharp versus basic on the dense grid

| Dataset | Floor | Conditions with more sharp coverage | Maximum added queries in one condition |
|---|---:|---:|---:|
| mnist | 0 | 0/1005 | 0 |
| mnist | 1 | 12/1005 | 101 |
| mnist | 100 | 2/1005 | 1 |
| fashion_mnist | 0 | 0/1005 | 0 |
| fashion_mnist | 1 | 17/1005 | 382 |
| fashion_mnist | 100 | 4/1005 | 9 |

This dense-grid comparison has its own declared scope. Original shared-width masks reproduce the frozen study exactly.

## Limits

These are post hoc guarded-certificate grid brackets. A last accepted grid point is not an exact real-arithmetic maximal width; a left-censored query has no measured positive frontier. The supplementary endpoint checks use the selected rectangle endpoint; the frozen certificate supplies the continuum guarantee. Seed summaries are descriptive paired results from shared evaluation images and overlapping training pools. The 16-width accuracy reference is an observed sampled maximum.
