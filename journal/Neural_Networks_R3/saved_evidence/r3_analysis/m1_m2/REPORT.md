# R3 numerical resolution of M1 and M2

The finite-threshold and exact-overlap analyses are complete. All 210 original R2 requested-region counts were reproduced exactly. The source archive and every R2 evidence file remain unchanged.

## M1: finite sufficient thresholds and validation relevance

For each query and each of the seven original upper widths, the calculation takes the minimum sufficient reversal bound over all competing classes whose limiting score exceeds the nearest-prototype score by the R2 numerical guard. The raw bound is `norm(r) * norm(A @ (Z_b-Z_a)) / delta`; its normalized value divides this bound by `norm(A,2)`. Minimization chooses the strongest of the existing Proposition 3 bounds. It introduces no new theorem. An infinite stored value denotes no guarded strictly competing class. A finite bound gives a sufficient penalty floor; it is not the first actual decision crossing.

The validation reference uses each seed's previously unused 5,000-row validation split, disjoint from its fitting rows. The MNIST validation rows are also disjoint from its 4,027 evaluation rows; Fashion-MNIST evaluation uses the separate official test set. All 96 original readouts (16 widths by six penalties) were scored against these validation labels, totaling 960 readout evaluations. No weights were fitted. A sampled readout is designated competitive if its validation accuracy is at least 95% of the best validation accuracy among that group's 96 archived pairs. Mean best validation accuracy is 87.644% for MNIST and 79.764% for Fashion-MNIST.

At every original width, the comparison uses the maximum competitive penalty at that same width. All five seeds have competitive pairs at `t/s_C = 0.5, 1, 2`; none have a competitive pair at the other four original endpoints. All thresholds and missing-comparator cases are retained in the CSV, with their full denominators.

| Dataset | t/s_C | Mean within-seed median bound / norm(A,2) | Mean within-seed 90th percentile | Range of maximum competitive penalty / norm(A,2) across seeds | Positive-bound query-width cases | Bounds below competitive maximum |
|---|---:|---:|---:|---:|---:|---:|
| MNIST | 0.5 | 1.87744 | 7.31273 | 1.876e-4 to 2.764e-4 | 16,212 | 0 |
| MNIST | 1 | 1.05618 | 1.18683 | 3.178e-5 to 3.442e-5 | 16,755 | 0 |
| MNIST | 2 | 1.00373 | 1.01653 | 8.119e-7 to 8.279e-7 | 16,755 | 0 |
| Fashion-MNIST | 0.5 | 1.64316 | 7.46935 | 7.888e-5 to 1.161e-4 | 25,063 | 0 |
| Fashion-MNIST | 1 | 1.15026 | 5.08809 | 2.909e-6 to 2.980e-5 | 33,135 | 0 |
| Fashion-MNIST | 2 | 1.08443 | 1.71095 | 0 to 8.333e-7 | 42,894 | 0 |

Thus zero of 150,814 positive-bound query-width cases at widths with competitive readouts has its sufficient threshold below the maximum sampled competitive penalty. The finite bound places the guaranteed reversal beyond the measured competitive penalties in this comparison. The 95% reference is post hoc and validation based; it is fully specified independently of the evaluation-query true labels.

The implementation checked all 175,027 positive-bound cases across all seven widths using the spectral resolvent at 1.001 times their bound and observed zero failures. A separate direct-solve recheck reconstructed 338 sampled bounds from the raw feature matrices and found a positive competing margin in every case.

## M2: exact unique contribution beyond finite checks

The primary limiting set L0 is exactly the R2 union of guarded limiting witnesses from the seven original widths within the requested upper width. F0 is the union of guarded original finite probes within the requested region. F1 adds every archived frontier and local-tail finite readout within that region. There are 1,161 archived readout records across the ten groups, compared with 960 in F0. F1 includes 12 local-tail records per group. Reconstructing their evaluation predictions gave zero mismatches across 8,241,228 query predictions.

The primary comparison keeps L0 fixed while strengthening the finite comparator. Counts below are five-seed mean percentages of the full query set; the difference-set columns therefore also express percentage-point contributions to the exclusion union. Floors are zero; all three original floors remain in the machine-readable results.

| Dataset | t/s_C | L0 exclusions (%) | F0 exclusions (%) | F1 exclusions (%) | L0 unique over F0 (pp) | L0 unique over F1 (pp) |
|---|---:|---:|---:|---:|---:|---:|
| MNIST | 0.25 | 36.459 | 36.712 | 36.712 | 0.045 | 0.045 |
| MNIST | 0.5 | 80.541 | 79.399 | 85.274 | 6.000 | 0.124 |
| MNIST | 1 | 83.233 | 80.070 | 88.095 | 8.026 | 0.000 |
| MNIST | 2 | 83.233 | 82.111 | 88.130 | 6.019 | 0.000 |
| Fashion-MNIST | 0.25 | 28.398 | 34.548 | 34.548 | 0.026 | 0.026 |
| Fashion-MNIST | 0.5 | 52.356 | 58.382 | 63.180 | 4.850 | 0.060 |
| Fashion-MNIST | 1 | 75.532 | 63.022 | 84.350 | 21.458 | 0.134 |
| Fashion-MNIST | 2 | 94.532 | 68.088 | 85.374 | 30.234 | 12.948 |

At `t=s_C`, the original limit union's unique contribution shrinks from 8.026 to 0 percentage points for MNIST and from 21.458 to 0.134 for Fashion-MNIST. The latter is 67 seed-query cases in total, with a five-seed SD of 0.078613 percentage points. These are exact mask differences, replacing the earlier lower-bound arithmetic from rounded aggregate counts.

An additional recorded variant extends the limiting set with all 67 dense-grid widths. At `t=s_C`, its unique contribution beyond F1 is 0% for MNIST and 0.148% for Fashion-MNIST. This is a distinct diagnostic; it does not replace the protected R2 figure or its original partition table. The earlier conversation's 0.136% was not used: all archived frontier readouts are included here, and the exact primary result is 0.134%.

For the comparison with only the zero-penalty endpoint model, the exact endpoint-limit difference set at `t=s_C` is 60.973% for MNIST and 46.338% for Fashion-MNIST. These improve upon the earlier aggregate lower bounds of 56.70 and 35.09 percentage points. The more informative all-archive comparison above should receive priority in the manuscript.

Finite sampling support is explicit: the archived high-penalty local-tail readouts use widths near `0.5s_C` and `s_C`, with penalties `10 norm(A_t,2)` and `100 norm(A_t,2)`. At `2s_C`, those additions still lie at widths no greater than `s_C`; the original finite probes at `2s_C` extend only to raw penalty 10,000. The large Fashion-MNIST residual at `2s_C` is measured under that exact sampling design.

## Reproduction and verification

From the project root:

```bash
python r3_analysis/m1_m2/run_analysis.py
python r3_analysis/m1_m2/verify_outputs.py
```

The first command reconstructs results in `r3_analysis/m1_m2/results/`; it reads `evidence/` and writes only inside its own analysis directory. The second command verifies hashes, 1,260 mask/count comparisons, exact recovery of all 210 R2 region counts, and 338 direct-solve finite-bound checks. The original source/evidence directories are read-only inputs to both scripts.

Key files:

- `protocol.json`: fixed post hoc analysis protocol and checksum recorded before numerical execution.
- `run_analysis.py`: executable numerical analysis.
- `results/m1_thresholds_per_seed.csv` and `results/m1_summary.csv`: threshold distributions and competitive-reference comparisons.
- `results/validation_reference_per_pair.csv`: every archived readout's validation score and competitive designation.
- `results/m2_overlap_per_seed.csv` and `results/m2_summary.csv`: exact counts, intersections, unique contributions and seed summaries.
- `results/*_K100.npz`: per-query thresholds, limiting/finite masks, validation predictions and normalization factors.
- `results/COMPLETE.json`: runtime, input hashes, successful checks and zero new fits.
- `results/SHA256_MANIFEST.json`: hashes of all result files.
- `verify_outputs.py` and `verification.json`: read-only arithmetic/integrity recheck and its recorded output.

## Interpretation limits

These results complete the requested threshold-placement and overlap computations. They establish no bound-guaranteed reversal within the sampled competitive validation range and quantify dependence of empirical exclusion increments on the finite comparator's sampling. A sufficient threshold does not identify the earliest actual reversal. Validation competitiveness is defined over the archived grid, not all possible hyperparameters. The new analyses do not resolve the editor's significance concern by themselves; the contribution must be stated as the supported analysis of agreement regions and its measured operating behavior.
