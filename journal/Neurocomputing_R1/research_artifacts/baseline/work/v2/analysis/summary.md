# Frozen experiment: descriptive results

The sharp and basic certificates produce identical masks over the complete predeclared experiment. Positive coverage occurs only at the smallest scaled upper width, s_C/16. All methods abstain at absolute upper width 1 and at scaled upper widths s_C/8 through 2s_C.

Every table uses all five seeds, including zero-coverage realizations. Entries are mean ± sample standard deviation in percentage points, with five seeds on shared evaluation queries: 4,027 MNIST reserve images and 10,000 Fashion-MNIST test images. No sampling confidence intervals or independent grid-cell inference are used.

## Exact denominator and audit accounting

The experiment contains 30 dataset/seed/budget groups, 630 parameter-region cells, and 1890 method-tagged cells. There are 4,418,505 query rectangles across those conditions; 587,703 are certified by sharp and basic. The Frobenius set is a subset in every cell.

Sharp alone contributes 5,289,327 certified rectangle/probe comparisons. Counting all three methods gives 1,460,692 certified method/query rectangles and 13,146,228 certified method/rectangle/probe comparisons. Deduplicating overlapping rectangles and methods within each dataset/seed/budget group gives 3,585,477 query/parameter comparisons. Every count has zero observed disagreements. These repeated-query checks assess the implementation at finite parameter values; the theorem establishes the continuum guarantee.

All 71 frozen result hashes match. 1676 of 1890 method cells have zero coverage; 306 are inapplicable under the declared positive-denominator condition. Both categories remain in every denominator.

## Main table: predeclared absolute width and smallest scaled width

| Dataset | K | Width upper bound | Penalty floor | Sharp / basic coverage (%) | Frobenius coverage (%) | Zero seeds: sharp / Frobenius | Endpoint agreement (%) | Readout accuracy (%) |
|---|---:|---|---:|---:|---:|---:|---:|---:|
| Fashion-MNIST | 50 | 1 (absolute) | 0 | 0.000 ± 0.000 | 0.000 ± 0.000 | 5 / 5 | 98.870 ± 0.163 | 57.090 ± 3.981 |
| Fashion-MNIST | 50 | 1 (absolute) | 1 | 0.000 ± 0.000 | 0.000 ± 0.000 | 5 / 5 | 98.856 ± 0.180 | 57.098 ± 3.983 |
| Fashion-MNIST | 50 | 1 (absolute) | 100 | 0.000 ± 0.000 | 0.000 ± 0.000 | 5 / 5 | 98.818 ± 0.199 | 57.108 ± 3.985 |
| Fashion-MNIST | 50 | 0.0625 × s_C | 0 | 99.326 ± 1.351 | 58.934 ± 53.827 | 0 / 2 | 99.948 ± 0.015 | 56.962 ± 4.054 |
| Fashion-MNIST | 50 | 0.0625 × s_C | 1 | 99.714 ± 0.483 | 58.934 ± 53.827 | 0 / 2 | 99.944 ± 0.022 | 56.960 ± 4.051 |
| Fashion-MNIST | 50 | 0.0625 × s_C | 100 | 99.772 ± 0.354 | 58.934 ± 53.827 | 0 / 2 | 99.940 ± 0.030 | 56.962 ± 4.054 |
| Fashion-MNIST | 100 | 1 (absolute) | 0 | 0.000 ± 0.000 | 0.000 ± 0.000 | 5 / 5 | 98.274 ± 0.653 | 63.436 ± 3.189 |
| Fashion-MNIST | 100 | 1 (absolute) | 1 | 0.000 ± 0.000 | 0.000 ± 0.000 | 5 / 5 | 98.242 ± 0.667 | 63.440 ± 3.186 |
| Fashion-MNIST | 100 | 1 (absolute) | 100 | 0.000 ± 0.000 | 0.000 ± 0.000 | 5 / 5 | 98.202 ± 0.695 | 63.440 ± 3.181 |
| Fashion-MNIST | 100 | 0.0625 × s_C | 0 | 79.086 ± 44.246 | 39.310 ± 53.831 | 1 / 3 | 99.912 ± 0.026 | 63.300 ± 3.221 |
| Fashion-MNIST | 100 | 0.0625 × s_C | 1 | 79.630 ± 44.519 | 39.310 ± 53.831 | 1 / 3 | 99.908 ± 0.029 | 63.300 ± 3.221 |
| Fashion-MNIST | 100 | 0.0625 × s_C | 100 | 98.656 ± 2.219 | 39.310 ± 53.831 | 0 / 3 | 99.906 ± 0.032 | 63.298 ± 3.223 |
| Fashion-MNIST | 200 | 1 (absolute) | 0 | 0.000 ± 0.000 | 0.000 ± 0.000 | 5 / 5 | 97.800 ± 0.534 | 68.652 ± 1.789 |
| Fashion-MNIST | 200 | 1 (absolute) | 1 | 0.000 ± 0.000 | 0.000 ± 0.000 | 5 / 5 | 97.778 ± 0.554 | 68.648 ± 1.780 |
| Fashion-MNIST | 200 | 1 (absolute) | 100 | 0.000 ± 0.000 | 0.000 ± 0.000 | 5 / 5 | 97.744 ± 0.586 | 68.648 ± 1.787 |
| Fashion-MNIST | 200 | 0.0625 × s_C | 0 | 79.056 ± 44.226 | 36.774 ± 50.516 | 1 / 3 | 99.804 ± 0.061 | 68.506 ± 1.686 |
| Fashion-MNIST | 200 | 0.0625 × s_C | 1 | 79.544 ± 44.471 | 36.794 ± 50.541 | 1 / 3 | 99.804 ± 0.061 | 68.506 ± 1.686 |
| Fashion-MNIST | 200 | 0.0625 × s_C | 100 | 98.542 ± 2.257 | 36.804 ± 50.553 | 0 / 3 | 99.804 ± 0.061 | 68.506 ± 1.686 |
| MNIST | 50 | 1 (absolute) | 0 | 0.000 ± 0.000 | 0.000 ± 0.000 | 5 / 5 | 97.924 ± 0.548 | 60.959 ± 4.213 |
| MNIST | 50 | 1 (absolute) | 1 | 0.000 ± 0.000 | 0.000 ± 0.000 | 5 / 5 | 97.720 ± 0.519 | 60.869 ± 4.190 |
| MNIST | 50 | 1 (absolute) | 100 | 0.000 ± 0.000 | 0.000 ± 0.000 | 5 / 5 | 97.477 ± 0.587 | 60.750 ± 4.230 |
| MNIST | 50 | 0.0625 × s_C | 0 | 99.940 ± 0.038 | 78.287 ± 43.794 | 0 / 1 | 99.955 ± 0.032 | 61.381 ± 4.173 |
| MNIST | 50 | 0.0625 × s_C | 1 | 99.940 ± 0.038 | 78.287 ± 43.794 | 0 / 1 | 99.955 ± 0.032 | 61.381 ± 4.173 |
| MNIST | 50 | 0.0625 × s_C | 100 | 99.940 ± 0.038 | 78.287 ± 43.794 | 0 / 1 | 99.955 ± 0.032 | 61.381 ± 4.173 |
| MNIST | 100 | 1 (absolute) | 0 | 0.000 ± 0.000 | 0.000 ± 0.000 | 5 / 5 | 97.825 ± 0.292 | 70.176 ± 2.798 |
| MNIST | 100 | 1 (absolute) | 1 | 0.000 ± 0.000 | 0.000 ± 0.000 | 5 / 5 | 97.651 ± 0.394 | 70.102 ± 2.824 |
| MNIST | 100 | 1 (absolute) | 100 | 0.000 ± 0.000 | 0.000 ± 0.000 | 5 / 5 | 97.393 ± 0.555 | 69.988 ± 2.809 |
| MNIST | 100 | 0.0625 × s_C | 0 | 99.911 ± 0.062 | 58.679 ± 53.574 | 0 / 2 | 99.935 ± 0.038 | 70.549 ± 2.566 |
| MNIST | 100 | 0.0625 × s_C | 1 | 99.911 ± 0.062 | 58.679 ± 53.574 | 0 / 2 | 99.935 ± 0.038 | 70.549 ± 2.566 |
| MNIST | 100 | 0.0625 × s_C | 100 | 99.911 ± 0.062 | 58.679 ± 53.574 | 0 / 2 | 99.935 ± 0.038 | 70.549 ± 2.566 |
| MNIST | 200 | 1 (absolute) | 0 | 0.000 ± 0.000 | 0.000 ± 0.000 | 5 / 5 | 97.825 ± 0.278 | 77.259 ± 2.154 |
| MNIST | 200 | 1 (absolute) | 1 | 0.000 ± 0.000 | 0.000 ± 0.000 | 5 / 5 | 97.651 ± 0.306 | 77.169 ± 2.136 |
| MNIST | 200 | 1 (absolute) | 100 | 0.000 ± 0.000 | 0.000 ± 0.000 | 5 / 5 | 97.363 ± 0.314 | 77.050 ± 2.117 |
| MNIST | 200 | 0.0625 × s_C | 0 | 99.856 ± 0.027 | 0.000 ± 0.000 | 0 / 5 | 99.916 ± 0.014 | 77.646 ± 2.029 |
| MNIST | 200 | 0.0625 × s_C | 1 | 99.856 ± 0.027 | 0.000 ± 0.000 | 0 / 5 | 99.916 ± 0.014 | 77.646 ± 2.029 |
| MNIST | 200 | 0.0625 × s_C | 100 | 99.866 ± 0.033 | 0.000 ± 0.000 | 0 / 5 | 99.916 ± 0.014 | 77.646 ± 2.029 |

## Numerical checks

The minimum certified unscaled margin is 1.46580475235e-05; its cell is {'dataset': 'fashion_mnist', 'seed': 44, 'K': 200, 'width_index': 1, 'lambda_lower': 0, 'method': 'cancellation_frobenius', 'certified': 8623, 'near_nearest_distance_ties': 0, 'minimum_certified_raw_margin': 1.4658047523541384e-05, 'minimum_certified_margin_guard_ratio': 51145.06721222982}. The smallest ratio of a certified margin to the declared numerical guard is 51145.0672122. All 30 groups have distinct prototype images, and all 480 probed feature matrices have full numerical column rank under the frozen SVD threshold.

## Evidence and source trace

`certificate_metrics_before_labels.csv` supplies certificate counts and region applicability. `endpoint_accuracy_and_fidelity.csv` supplies agreement and true-label accuracy counts. `certificate_accuracy.csv` supplies certified-subset correctness, with undefined conditional accuracy retained as an empty field when the certified set is empty. Archived `predictions_before_labels.npz` files establish exact mask equality, subset nesting, finite-probe deduplication, and numerical margins. `source_trace.json` records all input hashes. `analyze.py` reproduces all analysis tables and figures without changing or fitting the archived models.

## Limitations

Five seed realizations share evaluation queries, so the stated SD measures seed variation. The certified events guarantee agreement with the nearest-prototype label, and endpoint classification accuracy is measured separately against the dataset label. All bounds and audits use float64 arithmetic; outward-rounded interval verification is outside this execution. The selected data are two image benchmarks and random prototype subsets. Absolute width 1 and all scaled widths at least s_C/8 have zero observed certificate coverage. The sharp bound gives no realized mask improvement over the basic bound in this grid.
