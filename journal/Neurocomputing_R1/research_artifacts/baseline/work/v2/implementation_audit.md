# Independent implementation and completed-output audit

**Verdict: PASS.** The frozen executable implements the reviewed rectangle certificate and the declared experimental protocol. Independent reconstruction of every reported endpoint and certificate count agrees with the archived predictions, masks, and raw evaluation labels. No material implementation defect was found.

Audit date: 2026-11-06. Reviewer: independent theory/implementation agent. The audit did not change production source, protocol, inputs, predictions, masks, weights, or results. Held-out outcomes were inspected only after `results/COMPLETE.json` existed.

## 1. Frozen materials and provenance

The SHA-256 values for `protocol.json`, `run_experiment.py`, `certificate.py`, `synthetic_checks.json`, and `independent_theory_review.md` match `FREEZE.json`. All 11 declared data/input hashes match. All 71 entries in `results/MANIFEST_SHA256.json` match, both before and after the independent completed-output audit.

All 30 prediction archives match their individual pre-label receipts. Each receipt precedes the global `ALL_PREDICTIONS_FROZEN.json` timestamp; the global receipt precedes `COMPLETE.json`. Source inspection confirms that all predictions and masks are computed and hashed before the scoring function indexes evaluation targets. MNIST's complete training-label array is loaded to obtain fitting labels, and its reserved entries are excluded from fitting and from the later scoring operations until the global receipt is written. Fashion-MNIST test labels are first read by the post-freeze scoring function. Saved MNIST evaluation targets equal the raw labels at the declared reserved IDs; saved Fashion-MNIST targets equal the official test-label file.

## 2. Split, preprocessing, model, and grid audit

- Every group has 20,000 training rows and 5,000 validation rows with disjoint IDs. MNIST's 4,027 reserved evaluation IDs are absent from every training and validation split. Fashion-MNIST evaluates all 10,000 official test rows.
- Prototype IDs correspond exactly to the archived training-row indices. Budgets 50, 100, and 200 are nested within each dataset and seed. MNIST's 100-prototype setting, training IDs, and validation IDs equal the earlier frozen study; the extra 100 prototypes come from remaining training rows. Fashion-MNIST uses the declared seed and prefix rule.
- Image intensities are converted to float64 and divided by 255. The flattening convention agrees with the protocol. Both training and query inputs use the same coordinates.
- Training Gaussian activations are unscaled, with selected center self-activations set to one. The readout has no intercept. Its positive-penalty singular-value filter is `s/(s*s+lambda)`; its zero-penalty filter is the declared pseudoinverse with cutoff `max(N,K)*eps*smax`. All 480 saved factorizations have numerical rank equal to their prototype budget.
- Query Gaussian rows are divided by their positive largest activation through squared-distance subtraction before exponentiation. This operation preserves the class argmax and avoids wholesale query underflow.
- The seven width upper bounds, three penalty lower bounds, and nine finite probe configurations per rectangle match the frozen protocol. Independent exact float-value lookup finds each archived probe; the executable's nearest-index lookup therefore selects the intended configuration without substitution.
- The archive contains 16 distinct probe widths and six penalties per group: 480 feature factorizations and 2,880 fitted readouts over 30 groups. The 630 endpoint rows represent seven endpoint widths and three penalty floors per group; they are not the full fit count.

## 3. Certificate implementation

The implementation uses `E = H - S`, separates prototype rows from non-prototype rows, and forms `V = E_C Y_C`, `P = E_non.T Y_non`, and `Q = E.T (E Y_C)`. The non-prototype restriction in `P` is correct. The lower eigenvalue bound is `mu = max(1-beta, 0)^2`; clipping occurs before squaring. A nonpositive `mu+lambda0` causes abstention.

The sharp pair constant equals the maximum of the penalty-floor majorant norm and its infinite-penalty limit. The basic and cancellation-aware Frobenius constants match the independent mathematical derivation. Their archived hierarchy is satisfied; the largest positive sharp-minus-basic difference is 7.703719777548943e-34, within the declared floating-point comparison tolerance. Basic never exceeds the Frobenius constant. The certificate masks satisfy Frobenius subset basic subset sharp in every group and rectangle. They are also nested under decreasing width upper bounds and increasing penalty lower bounds.

The query implementation compares every competing class, uses the one-unit nearest-prototype contribution in the lower margin, and ignores only the reference class's self-comparison. It enforces the declared nearest-distance tie rule and the strict margin guard `gap > 1e-10*(1+abs(lhs)+abs(rhs))`. Inapplicable rectangles produce no certified observations. Missing prototype classes remain in the competitor array.

An independent implementation on 450 synthetic endpoint cases reproduces all 14,850 production method/query mask entries exactly, with maximum checked-array discrepancy zero. This check accessed no held-out arrays. The separate pre-freeze theory validation covered 117,975 certified synthetic parameter checks with zero violations.

## 4. Independent reconstruction of reported outcomes

| Check | Independently verified result |
|---|---:|
| Endpoint CSV rows recomputed | 630 |
| Certificate accuracy CSV rows recomputed | 1,890 |
| Pre-label certificate metric rows recomputed | 1,890 |
| Prediction archive groups checked | 30 |
| Certified finite-probe exposures | 13,146,228 |
| Certified finite-probe label-agreement violations | 0 |
| Smallest certified raw margin | 0.000014658047523541384 |
| Largest certified raw margin | 0.9998792191273603 |
| Smallest finite raw margin over all query/method/rectangles | -257002140.17266598 |

Every count in `endpoint_accuracy_and_fidelity.csv`, `certificate_accuracy.csv`, and `certificate_metrics_before_labels.csv` was recomputed from the saved arrays. This includes overall model accuracy, nearest-prototype accuracy, Gaussian prototype-vote accuracy, pairwise agreement counts, the two directions of accuracy change, certified/uncertified correct counts, certificate coverage, probe counts, and certified violations. All values match. The 13,146,228 probe exposures repeat observations across methods and parameter rectangles; they are a verification workload count.

The minimum certified raw margin occurs at Fashion-MNIST seed 44, K=200, width index 1 (`t=0.5079063152252199`), penalty floor 0, Frobenius certificate, query ID 6801. Its margin exceeds the fixed 1e-10 base guard by more than five orders of magnitude. All certified margins are finite and strictly positive. Saved readout weights are finite.

## 5. Reporting correction

`environment.json` captures `threadpool_info()` before entering the one-thread context. Its reported ambient thread count is not the thread count used by the training loop. The source wraps the full experiment in `threadpool_limits(1)`, as declared. Describe this as a configuration established by source inspection; do not cite the environment snapshot as evidence of the active in-loop thread count. This metadata issue does not change model fitting, certificate evaluation, or any recomputed result.

## 6. Audit boundaries

The theorem establishes the continuum result in real arithmetic. The float64 implementation uses an explicit guard and all archived certified finite probes agree with the fitted classifier. A formal interval enclosure of all rounding operations was not implemented. The audit independently checked the mathematics, production source, synthetic implementation behavior, archive integrity, splits, grids, and all outcome counts; it did not repeat all 480 production singular-value factorizations. Novelty and journal suitability are handled by the separate literature and editorial reviews.

## Reproduction artifacts

- `work/v2/independent_theory/audit_completed_experiment.py`: read-only completed-output verification script.
- `work/v2/independent_theory/completed_experiment_audit.json`: machine-readable verification results and group-level checks.
- `work/v2/independent_theory/production_implementation_synthetic.json`: independent synthetic comparison with the production certificate module.
- `work/v2/independent_theory_review.md`: independent theorem review, proof, and edge cases.
