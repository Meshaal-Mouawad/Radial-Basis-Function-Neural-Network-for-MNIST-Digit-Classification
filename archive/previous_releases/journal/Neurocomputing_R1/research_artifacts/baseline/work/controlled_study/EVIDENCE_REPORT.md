# Completed controlled experiment evidence

New measurements executed on 6 November 2026. The supplied 10 April 2026 report and MATLAB code remain unchanged.

## Design and execution

Five seeds each use a stratified 20,000-image training subset and a disjoint 5,000-image validation subset drawn from the supplied 60,000-image training pool. All five use the same supplied 10,000-image test set. Each seed has 100 randomly chosen training prototypes. The frozen grid has four Gaussian widths and seven penalties, giving 140 validation fits. Validation selection is recorded before test scores are computed. Test conditions and the same-budget nearest-prototype comparator were declared before execution.

## Test accuracy

| Condition | Mean ± sample SD (%) | Minimum–maximum (%) |
|---|---:|---:|
| nearest_prototype | 70.564 ± 2.726 | 66.76–73.58 |
| fixed_1_pinv | 70.294 ± 2.900 | 66.42–73.47 |
| fixed_1_lambda_1 | 70.208 ± 2.899 | 66.42–73.44 |
| scale_1_pinv | 88.550 ± 0.263 | 88.14–88.80 |
| scale_1_lambda_1 | 88.062 ± 0.322 | 87.54–88.36 |
| validation_selected | 88.548 ± 0.267 | 88.13–88.80 |

Each run denominator is 10,000 images; SD summarizes split and prototype draws. The five test evaluations are correlated through their shared test images and overlapping training pools.

## Findings and interpretation

At the same unregularized SVD readout, distance-scaled width increases accuracy by 18.256 percentage points on average. This matched comparison holds prototypes, training subset, and readout fixed; the width changes.
Across 35 positive-penalty conditions, batch ridge and single-pass RLS have zero test-label disagreements. The largest relative Frobenius weight error is 9.22991e-14; the largest absolute test-score difference is 2.80925e-13. The calculation validates the known lambda=1/alpha relationship under these fixed features.
All five validation selections use the full distance-scale width. Four select unregularized SVD; seed 33 selects lambda=0.01. The scale is the median off-diagonal pairwise prototype distance divided by sqrt(2), giving widths between 7.1427 and 7.3904.
The closest-prototype baseline uses the same 100 random prototype labels. It controls prototype budget and distance representation, without training an output readout. It is not a full-training-set nearest-neighbor baseline.

## Evidence boundaries

The study measures one image dataset, one prototype budget, random center selection, and one fixed validation grid. It establishes a controlled empirical contrast and numerical equivalence. It does not establish a new solver or a new RBF principle. The April report accuracy values are not treated as reproduced measurements.
Timing is separated into distance construction, activation exponentiation, factorization, and RLS readout updating. The solver timings use precomputed features and a single execution, so they are descriptive runtime records. The script retains the full features for the equivalence audit; any streaming-state memory formula would be analytical, not a measured peak-memory claim.

## Reproduction

Run `python run_study.py --data-dir <repository>/Code --output-dir <new-output-directory>` with NumPy, SciPy, scikit-learn, and threadpoolctl. The two original MAT hashes are checked before computation. The script uses float64 conversion before dividing by 255 and MATLAB-compatible image flattening. Run `python analyze_results.py` to reproduce descriptive summaries and figures from the recorded default results directory.
The protocol JSON hash, run source hash, dependency versions, data hashes, and completed result hashes are recorded. Split, prototype, and test indices and all five diagnostic score matrices per seed are retained in the prediction archives. A synthetic ridge/RLS equivalence test precedes the dataset computation.

## Editorial use

Use these new measurements for a manuscript about bandwidth control and matched batch/recursive readouts. Preserve the reported April results only as historical claims in an external audit. Novelty and journal readiness must be judged against prior RBF, regularized least-squares, and online-learning literature.
