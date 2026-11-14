# Independent numerical audit of R3

**Outcome: PASS for the reconstructed numerical claims.** The independent script imports neither R3 analysis runner. It rebuilds Gaussian features from the preserved image payloads and reconstructs scores from archived R2 weights. It writes only within this audit directory.

## Verified quantities

| Check | Reconstructed scope | Result |
|---|---:|---|
| M3 endpoint predictions | 140,270 labels | Exact agreement with archive |
| Equal-cardinality selectors | 120 masks across 20 settings | Exact mask agreement |
| M3 per-seed accuracy records | 140 rows | Correct |
| Predicted and true class counts | 1,400 rows | Exact agreement |
| M3 five-seed mean and sample SD | All summary rows for coverage, accuracy, paired difference | Correct |
| Validation reference | 4,800,000 labels from 960 archived readouts | Exact predictions and accuracies |
| Sufficient reversal thresholds | 490,945 query-width cases | Finite masks identical; threshold values agree numerically |
| Finite reversals above threshold | 175,027 checks | All strict competing margins positive |
| M2 original and expanded finite witness unions | 210 regions | Exact mask agreement |
| R2 original exclusion unions | All 210 frozen rectangle records | Exact count reproduction |

The maximum relative threshold difference was approximately 1.24e-10. The independent calculation sums class-specific feature rows directly, while the analysis runner multiplies the feature matrix by one-hot labels. All finite/infinite threshold classifications and every tested reversal agree.

## Findings retained in the manuscript

1. No sufficient reversal threshold falls below the largest sampled competitive penalty at the same width. The comparison covers 150,814 strict-limit query-width cases in 30 eligible dataset/seed/width settings. Competitive membership uses the newly evaluated disjoint validation partitions.
2. The MNIST endpoint readout at t=s_C predicts class 1 for every evaluation query. Its higher certified-subset accuracy therefore reflects the composition of the selected subset, with the reported class counts confirming the concentration.
3. All selectors use the exact per-seed certificate cardinality and select without evaluation labels. Raw and row-normalized score margins produce the same class predictions and can produce different rankings; both comparisons are correctly retained.
4. At t=s_C and floor zero, the original-width limiting witness adds 0% on MNIST and 0.134 percentage points on Fashion-MNIST beyond all archived finite checks. Adding the dense-width limit witnesses raises the Fashion-MNIST unique contribution to 0.148 percentage points. These refer to different witness sets.
5. The earlier `combined_original` column represented the endpoint limit union with original finite checks, not the full R2 prefix-limit union. The implementation renamed it `endpoint_limit_plus_original_finite`. The authoritative R2 reproduction column is `r2_union`; it reproduces 88.095356% MNIST and 84.480000% Fashion-MNIST at t=s_C.

## Reproduction

From a directory containing `evidence/` and `r3_analysis/`:

```bash
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 PYTHONDONTWRITEBYTECODE=1 \
  python r3_analysis/independent/verify_r3.py
```

The script requires NumPy, SciPy and threadpoolctl. `verification.json` contains counts, per-group results, script hash and elapsed time. `verification.log` records the completed run.

## Audit scope

This audit verifies numerical reconstruction and the reported comparisons. It uses preserved R2 readouts and performs no new model training. The proof verification and full R2 baseline checks are recorded separately. Numerical success does not close the editorial significance question; the comparison findings above determine the supported interpretation.
