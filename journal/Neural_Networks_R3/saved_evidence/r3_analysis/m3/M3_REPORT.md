# R3 M3 — Equal-coverage selectors and class concentration

## Decision

The certificate selects higher-accuracy queries than uniform random selection and the ordinary score/distance margin selectors in all four reported settings. Agreement-gated distance selection is more accurate in three settings and selects exactly the same set in the fourth. Thus the supported empirical result is selective enrichment relative to those ordinary baselines; the strongest evaluated simple baseline does not establish a certificate accuracy advantage. The continuous-band guarantee remains the certificate-specific result.

## Verified setup

- Two datasets, five original seeds each, K = 100; endpoint widths t/s_C = 0.5 and 1.
- Endpoint readout penalty is 10 ||A_t||_2; certified set refers to [0.99t,t] × [10 ||A_t||_2, infinity).
- Every selector uses exactly the certificate cardinality within each dataset–seed–width. All ten groups and both endpoints are retained.
- Selection uses model scores, distances, labels of prototypes, and deterministic query-ID ties. Evaluation labels are used only for scoring.
- Primary score margin is the difference between the largest two **raw fitted scores**. The archive uses a positive query-wise scaling for stable prediction; that scaling preserves argmax but changes across-query margin ranking. Its separate sensitivity result is preserved in the CSV.
- Prototype class-distance margin is squared distance to the closest differently labelled prototype minus squared distance to the nearest prototype.
- Gated selectors first restrict to queries whose endpoint readout and nearest-prototype labels agree, then rank by the same raw-score or distance margin.
- Values below are means ± sample SD across five seeds. Reported paired differences are also in `summary.csv`; this is post hoc descriptive evaluation, not a prospective selector tuning study.

## Exact matched-size random expectation

For fixed correctness indicators G_1,...,G_N and a uniformly selected size-m subset S, E[1/m sum_{i in S} G_i] = (1/m) sum_i G_i P(i in S) = (1/N) sum_i G_i, since P(i in S)=m/N. Thus full-query accuracy is the exact expected random-subset accuracy at every matched m, without Monte Carlo approximation.

## Endpoint accuracy (%)

| Dataset | t/s_C | Certificate | Random expectation | Score margin | Distance margin | Gated score | Gated distance |
|---|---:|---:|---:|---:|---:|---:|---:|
| MNIST | 0.5 | 69.09 ± 5.36 | 15.60 ± 1.35 | 67.87 ± 4.64 | 41.11 ± 3.52 | 69.17 ± 5.26 | 85.55 ± 9.05 |
| MNIST | 1 | 68.93 ± 5.28 | 11.77 ± 0.00 | 66.05 ± 4.56 | 28.05 ± 6.08 | 68.93 ± 5.28 | 68.93 ± 5.28 |
| Fashion-MNIST | 0.5 | 75.27 ± 2.96 | 45.06 ± 2.57 | 65.19 ± 4.97 | 60.11 ± 3.70 | 76.13 ± 2.25 | 79.34 ± 3.51 |
| Fashion-MNIST | 1 | 64.65 ± 4.41 | 29.86 ± 6.34 | 57.21 ± 7.67 | 31.01 ± 21.19 | 64.47 ± 5.09 | 82.94 ± 9.38 |

Coverage means are 16.88% / 16.79% for MNIST and 40.09% / 14.94% for Fashion-MNIST at t/s_C = 0.5 / 1. The certificate minus gated-distance differences are −16.47 / 0.00 percentage points for MNIST and −4.06 / −18.29 points for Fashion-MNIST.

## Class concentration

- **MNIST at t=s_C:** every endpoint prediction is class 1 in every seed. The exact evaluation set has 474 class-1 labels among 4,027 queries (11.7705488%). Certificate masks equal the entire endpoint-agreement pool for every seed, so both gated selectors select the identical query set and have the identical 68.9341% mean accuracy. The reported enrichment therefore corresponds to selecting the nearest-prototype class-1 subset of a constant class-1 fitted predictor.
- **MNIST at t=s_C/2:** class 1 accounts for 95.36% of all endpoint predictions and 99.45% of certified predictions on average. Agreement-gated distance selection includes a broader prediction-class distribution and attains 85.55% mean accuracy.
- **Fashion-MNIST at t=s_C:** class 7 accounts for 80.94% of certified predictions on average, compared with 32.33% of full-query predictions. Full-query predictions concentrate in classes 6 (34.16%), 7 (32.33%) and 3 (16.03%).
- **Fashion-MNIST at t=s_C/2:** certified predictions are distributed over several classes, with class 7 at 30.97%, class 1 at 23.32%, and class 0 at 15.93%.
- Fashion-MNIST has exactly 1,000 evaluation labels per class; every constant-class predictor has 10% full-query accuracy. MNIST’s class-1 full-query majority reference is 11.7705488%. The modal training class is also class 1 for each MNIST seed; the balanced Fashion-MNIST training tie resolves to class 0. These references are calculated from the archived arrays, not external dataset descriptions.
- Full per-seed true and predicted class counts for every selector are in `results/class_counts.csv`; exact query-label counts are in `results/query_label_distribution.csv`.

## Verification

PASS: reconstructed 140,270 endpoint prediction labels from archived weights and raw features with exact agreement. The separate verification script reconstructed 20 ridge readouts from A_t and B_t, with maximum weight and score differences of 0.0 in this runtime. It verified all 140 selector result rows, 1,400 class-count rows, every ranking/cardinality, saved result hashes, and unchanged input hashes. No new model setting was fitted or tuned.

Run from the project root:

```bash
python r3_analysis/m3/run_m3.py --evidence evidence
python r3_analysis/m3/verify_m3.py --evidence evidence
```

The script accepts `--output`; the verifier accepts `--results`. Dependencies: NumPy, SciPy, threadpoolctl. The evidence tree is the extracted R2 computational supplement. Protocol, scripts, results and verification are owned by this M3 folder; original manuscript, figures, equations and data were not edited.

## Manuscript integration

Add the exact random-selection derivation and definitions of ordinary/gated selectors to Methods. Report a single equal-coverage table containing the gated-distance comparator as well as ordinary margins. Explain the MNIST constant-class behavior and exact equality of the certificate/agreement pool at t=s_C. Interpret enrichment and continuous-region certification separately; a general predictive-accuracy advantage is not supported by these comparisons.
