# Executed prospective RBF parameter-region study

**Status: COMPLETE.** The frozen study executed once on 6 November 2026, from approximately 18:46 to 18:48 Saudi time. All thirty dataset/seed/prototype-budget groups completed, and the execution session exited with code zero. No worker remains active for this study.

## Scientific object

The experiment evaluates sufficient certificates for agreement between a fixed RBF readout's predicted class and its nearest training prototype's class, uniformly over the parameter region 0 < sigma <= t and lambda >= lambda0. It compares the sharp class-pair certificate with a basic class-majorant certificate and a cancellation-aware Frobenius comparator on the same region. Class-labelled Gaussian votes are measured as a separate endpoint diagnostic.

The independent mathematical review establishes the sufficient condition and its assumptions. The finite experimental checks test implementation and practical coverage. They are not a discretization proof of the continuum result. Agreement with a prototype label is distinct from correctness against the true label.

## Protocol and execution record

- Five seeds: 11, 22, 33, 44 and 55.
- Two datasets: the globally reserved 4,027 MNIST training-pool images and the official 10,000-image Fashion-MNIST test set.
- Three nested random-prototype budgets: 50, 100 and 200.
- Seven width upper bounds: absolute one, and 0.0625, 0.125, 0.25, 0.5, 1 and 2 times the training-prototype distance scale.
- Three penalty lower bounds: 0, 1 and 100.
- Three width probe fractions: 0.5, 0.75 and 1.
- Penalty probe triples: 0/1/100; 1/10/100; and 100/1000/10000 for their corresponding lower bounds.
- 480 distinct feature-matrix SVD factorizations and 2,880 filtered readout fits, reusing factors across penalties.
- 630 primary rectangle endpoints and 1,890 certificate rows, including all three certificate methods.

The actual main-execution duration was 123.20 seconds. The code runs all experimental fitting and certificate operations within `threadpool_limits(1)`. The environment JSON reports the libraries before that context is entered; it is not a capture of active in-context thread counts. Timings are descriptive execution records, not a repeated performance benchmark.

## Verified results and preservation

All three methods together certified **1,460,692 method/query rectangles**. The finite audit checked **13,146,228 certified query/parameter combinations**, with **zero certified label disagreements**. These counts reuse queries, parameter regions, seeds and methods and must not be interpreted as independent population observations.

A post-execution audit recomputed every certified finite-probe comparison from the saved predictions, verified the expected mask containment (count implies basic; basic implies sharp), and recomputed all 630 endpoint correctness and nearest-prototype agreement counts. All checks passed.

All 71 result-manifest file hashes match. The frozen protocol, runner and certificate hashes still match `FREEZE.json`; all eleven protocol input hashes match. All 45 files covered by the earlier completed-study manifest remain unchanged. Within each seed, training and validation sets are disjoint, all prototypes belong to training, and the MNIST reserve is excluded from every fit and validation set.

Every selected prototype image was distinct within its group's selected set. Every numerical reference matrix retained full column rank under the declared SVD cutoff. These checks are recorded in the saved arrays and `execution_verification.json`; no prototype was resampled after observing an outcome.

## Target-label chronology

The runner generated and hashed all thirty groups' predictions and certificate masks before using evaluation targets for scoring. `results/ALL_PREDICTIONS_FROZEN.json` is dated 15:48:05.512589 UTC; true-label metrics were computed afterward. The full MNIST label array was loaded because training labels share its MATLAB variable; reserved entries were not used for fitting, selection or metric computation before the final scoring phase. Fashion-MNIST test labels were decoded in that final phase.

There was no evaluation-based hyperparameter or certificate selection. The complete declared grid is retained, including inapplicable bounds and zero coverage. The detailed coverage and accuracy summaries are prepared independently from these immutable results in `work/v2/analysis/`.

## Source identities

| File | SHA-256 |
|---|---|
| Frozen protocol | 63aa7750d07f2bc74e46e01cf7b1866f487504f64ff325ff94135f122bca36d5 |
| Executed runner | 52e60a9221a6610e2c68c64d06f5781489267dd9852fdc858abdda9796f10065 |
| Executed certificate implementation | 97e4890a185573bed1ff2229cccbcb476e0eb9036084b4807c37e885e3428603 |
| Final synthetic implementation checks | 364efd5f480d1e4c16e1e17645ba69440b4f5a943d1739f4bc8d54e02ba41bc5 |

The frozen mathematical review hash is also retained in `FREEZE.json`. It identifies the review used at execution time; later editorial additions to that review do not alter the executed code or protocol.

## Reproduction

Retain the workspace-relative tree because the executed runner resolves inputs against its project root: `work/v2/experiment/`, `work/v2/design/`, `work/v2/data/fashion_mnist/`, `work/controlled_study/results/`, and `repository/Code/`. The protocol lists every required input and expected hash. Copying the runner to a different directory without its tree is not a faithful reproduction setup.

A synthetic-only implementation check, which reads no dataset, is:

```bash
python work/v2/experiment/run_experiment.py --self-test-only
```

For an intentional new full execution, preserve this completed release and choose an empty output directory:

```bash
python work/v2/experiment/run_experiment.py \
  --protocol work/v2/experiment/protocol.json \
  --freeze work/v2/experiment/FREEZE.json \
  --output-dir rerun/parameter_region_results \
  --execute
```

The required core packages are NumPy, SciPy, scikit-learn and threadpoolctl. The accompanying `requirements.txt` records the inspected installed versions: NumPy 2.3.5, SciPy 1.17.0, scikit-learn 1.8.0 and threadpoolctl 3.6.0. No new deep-learning framework is required.

## Numerical scope

The theorem is expressed in real arithmetic. The implementation evaluates strict margins in float64 with the predeclared guard `1e-10*(1+abs(lhs)+abs(rhs))` and abstains at near-nearest-distance ties using a relative threshold of 1e-12. It does not implement outward-rounded interval arithmetic. The numerical-margin audit reports the observed distance from those guards separately. The true-class accuracy of a certified decision is reported as a measured outcome, not as part of the certificate's guarantee.
