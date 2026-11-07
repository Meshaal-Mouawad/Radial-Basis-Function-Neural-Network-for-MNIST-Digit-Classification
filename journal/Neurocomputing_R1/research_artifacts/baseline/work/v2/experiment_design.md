# Prospective experiment design: faithful prototype explanations in RBF readouts

Date: 6 November 2026. Status: design proposal for the lead editor's freeze; no model fitting or reserved-outcome analysis has been performed by this workstream.

## Scientific target and interpretation

The primary target is a sufficient condition certifying that the fitted RBF readout predicts the class of its nearest labelled prototype **simultaneously for every 0 < sigma <= t and every lambda >= lambda0**. This is a continuum rectangle in width and penalty, not just the finite grid used for numerical validation. The class-labelled Gaussian kernel vote is a separate exact diagnostic.

The certificate concerns fidelity to the fitted model's decision. True-label correctness is a secondary outcome evaluated separately. The mathematical proof establishes a real-arithmetic sufficient condition; finite experiments check its implementation and practical coverage. A correct classification need not have a faithful nearest-prototype explanation.

The proposed sharp bound is compared against a looser class-majorant bound and a cancellation-aware Frobenius perturbation bound on the SAME continuum rectangle. A fitted pointwise bound would cover a different object and is not used to claim coverage dominance. Offline certificate preparation does not form H-transpose-H or solve the output readout, but timings remain descriptive unless a repeated benchmark is performed.

## Preserved baseline and untouched evaluation reserve

The original April 10 report, first controlled November study and all their source/prediction hashes remain unchanged. The five previous seeds are 11, 22, 33, 44 and 55. Each has 20,000 training IDs, 5,000 validation IDs and 100 center IDs in the 60,000-row training pool.

A read-only union of just these archived index arrays gives 55,973 previously used training/validation rows. Its complement is **4,027 global reserve rows**, unused by every prior fit and selection. Within-seed training/validation disjointness and center membership were rechecked. No reserve labels, per-row correctness, or model outputs were read.

- `design/reserved_training_ids.npy`: ascending zero-based original training-image indices, int64.
- SHA-256: `d38850e78c5faa4dfafd4c4c53f24d122162980d9717960a6002fb6527646e11`.
- `design/reserve_audit.json` records all five parent NPZ hashes and the audit.

Use this entire reserve as the primary prospective MNIST evaluation set after the new protocol, formulas, implementation and assertions are frozen. Existing validation subsets are development material. The original 10,000 test images have already been examined; any new measurements on them must be explicitly secondary/exploratory and cannot replace the reserve.

## Dataset provenance and independent transfer condition

The supplied MNIST image arrays have now been compared against the public IDX files listed in official Torchvision source. Both compressed downloads passed the listed MD5 checks. After moving the MATLAB image axis to the first dimension, all 60,000 training images and all 10,000 test images are pixel-identical and index-identical to those canonical payloads. A spatial transpose is not needed. Only image arrays were loaded; labels were not checked in this pre-freeze audit. `design/canonical_image_provenance.json` records the exact hashes and transformation.

Fashion-MNIST is the proposed second dataset: 60,000 training and 10,000 test images, 28×28 grayscale, ten apparel categories. Its same-dimensional representation permits the same algorithm and preprocessing while changing the semantic discrimination problem. Downloaded compressed files are obtained from the creators' Zalando repository and checked against its README MD5 list; acquisition records and the original MIT license are under `data/fashion_mnist/`. Held-out labels are not decoded before protocol freeze.

For Fashion-MNIST, use the same five seed values, a stratified 20,000-row training subset, and a stratified 5,000-row validation subset from the remaining 40,000 using seed+1,000. Use the official 10,000 test images for the prospectively frozen analysis. No choice should be selected using those test labels. All conditions can be evaluated as a declared grid without selecting a winner.

Sources actually inspected: official Torchvision dataset implementation, https://docs.pytorch.org/vision/stable/_modules/torchvision/datasets/mnist.html, lines 67–76 (MNIST mirrors/checksums) and 241–264 (Fashion checksums); Keras Fashion-MNIST documentation, https://keras.io/api/datasets/fashion_mnist/; creator repository https://github.com/zalandoresearch/fashion-mnist, README Get the Data table and license (accessed 6 November 2026). These sources establish acquisition and structure, not experimental outcomes.

## Bounded factor design

| Factor | Proposed frozen values | Reason |
|---|---|---|
| Data | MNIST reserve; Fashion-MNIST official test | Prospective original-task evaluation plus independent non-digit setting |
| Seeds | 11, 22, 33, 44, 55 | Preserve pairing and assess split/prototype sensitivity |
| Training budget | 20,000 per seed | Match baseline; isolate representation and explanation effects |
| Prototype budgets | 50, 100, 200 | Test whether certificate usefulness is limited to one arbitrary budget |
| Center rule | Random sampled training images, nested within each seed | Prototypes retain genuine class labels; nesting controls changes across budgets |
| Widths | Absolute 1; 0.0625, 0.125, 0.25, 0.5, 1, 2 times s_C | Cover localized, intermediate and broad regimes with a priori positions |
| Distance scale | s_C = median pairwise center distance / sqrt(2), training centers only | Existing interpretable scale |
| Output penalty | 0, 1, 100 | Unregularized, moderate and strong penalty; no unnecessary dense sweep |
| Fit | Float64 thin SVD, declared original cutoff for zero penalty | Same stable reference across conditions |
| Target | Class-labelled Gaussian vote; nearest-prototype label separately | Keep two distinct explanation claims separate |

This gives 2 × 5 × 3 × 7 = **210 feature factorizations** and **630 output fits**. SVD factors are reused across penalties; distance matrices are reused across widths. There is no reason to rerun the old 35 RLS checks because the new certificate question does not depend on whether the same ridge solution is computed in batch or recursively.

For MNIST nesting, preserve the exact existing 100 center IDs. Use their first 50 for K=50. For K=200, append 100 training IDs sampled from the non-center rows with a separately declared seed offset. For Fashion-MNIST, a single seeded 200-row permutation supplies prefixes 50/100/200. Freeze the offset and ordering in the executable protocol; do not change them after outcomes are seen. Recompute s_C within each budget.

One random-center rule is sufficient for this first mechanism test. A class-balanced center strategy is justified only if the literature or theory makes prototype class-count imbalance a target mechanism. Adding k-means would remove directly observed prototype labels and change the explanation object, so it should not be introduced as an automatic extra baseline.

## Exact candidate protocol and executable

The current executable proposal is `experiment/protocol_draft.json`, with `experiment/certificate.py` and `experiment/run_experiment.py`. It requires a lead-approved frozen protocol and `FREEZE.json` matching the protocol, runner and certificate source hashes before any real-data execution. The executed baseline is never overwritten.

The six penalty values used for finite verification are 0, 1, 10, 100, 1000 and 10000. For each lower bound lambda0, probe penalties are:

| lambda0 | Probe penalties |
|---|---|
| 0 | 0, 1, 100 |
| 1 | 1, 10, 100 |
| 100 | 100, 1000, 10000 |

Each rectangle is checked at sigma/t = 0.5, 0.75 and 1, giving nine finite probe pairs. Duplicate widths are fitted once. Across thirty dataset/seed/budget groups this gives 480 SVD factorizations and 2,880 inexpensive filtered readouts. The primary endpoint design remains 630 width/penalty configurations. These finite checks are implementation evidence, not a proof of the continuum claim.

## Candidate sharp continuum certificate

Write H=S+E, where S selects the training rows used as prototypes, so E is elementwise nonnegative and its prototype self-response entries are zero. Let Yc hold the prototype class indicators, E_C the prototype-row block, and E_non the remaining rows. Define:

- V = E_C Yc.
- P = E_non-transpose Y_non.
- Q = E-transpose (E Yc).
- beta = maximum row sum of E_C; mu = max(1-beta,0)^2.

For each pair of distinct classes a,b, sum the corresponding columns of V, P and Q. The sharp pair constant is the larger of the Euclidean norms of `(abs(lambda0-1) V_pair + (lambda0+1) P_pair + Q_pair)/(mu+lambda0)` and `V_pair+P_pair`.

For a query, choose its unique nearest prototype class a and use r_j = exp(-(d_j^2-d_nearest^2)/(2t^2)). For every competing class b, require `1-sum_{prototype label b} r_j > norm(r)*pair_constant`. This holds with the declared strict numerical guard. The proof workstream independently verifies the interval and penalty-uniform argument.

The basic class-majorant comparator uses the norm of `((lambda0+1)(V_pair+P_pair)+Q_pair)/(mu+lambda0)`. The cancellation-aware Frobenius comparator uses `((lambda0+1)*eta*sqrt(n_a+n_b)+eta^2*sqrt(k_a+k_b))/(mu+lambda0)`, with eta=norm(E)_F, training class counts n, and prototype class counts k. All three evaluate the same lower query margin and continuum domain.

Abstain whenever mu+lambda0 is zero. Also abstain when the two closest squared distances differ by at most `1e-12*max(1,d_first^2,d_second^2)`. Certification requires `lhs-rhs > 1e-10*(1+abs(lhs)+abs(rhs))` for every competing class. All abstentions and zero-coverage cells remain in the reported result grid.

## Stable query evaluation and label chronology

At small widths, unscaled Gaussian query activations can underflow. The executable subtracts the nearest squared distance before exponentiation. This multiplies a query's feature row by a positive common factor in exact arithmetic, preserving decisions and the homogeneous certificate. Training H remains unscaled.

All thirty groups' predictions, weights, certificate masks and indices are saved and hashed before any held-out target value is used to compute accuracy. `ALL_PREDICTIONS_FROZEN.json` records this boundary. Evaluation labels are saved separately in the final phase. Predictions, certificate validity and nearest-prototype agreement do not require the query's true class.

## Prespecified measurements

For each dataset, seed, K, width upper bound, penalty lower bound and certificate, retain evaluation count, applicability, certified count and fraction, number of finite probe pairs, and all certified/readout-label disagreements. Any certified disagreement stops execution while retaining the failing record.

At each primary rectangle endpoint, report actual nearest-prototype/readout agreement, Gaussian-vote/readout agreement, readout accuracy, reference-explanation accuracy, and both directions of true-label correctness change. Separately report correct and incorrect outcomes among certified and uncertified queries. Higher true-label accuracy does not establish explanation faithfulness.

Record proposed-minus-basic and proposed-minus-generic coverage differences on the same queries, all zero-coverage models, beta, mu, perturbation norms, activation summaries, singular values, class counts and computation phases. Archive the trained weights and label-free decisions so that finite comparison checks can be reconstructed.

Five seeds reuse evaluation subjects and overlap in training data; seed SD therefore describes draw variation rather than independent populations. Never count grid predictions as independent test subjects. Present datasets and width regimes separately, with complete supplementary tables.

## Checks already performed and execution boundary

The production certificate implementation passed synthetic checks on 4,500 query rectangles. Across the three methods, 3,900 method/query rectangles were certified; no certified probe disagreement was observed. Sharp constants were no larger than basic constants apart from a maximum 5.6e-17 floating-point difference. A contradictory-duplicate counterexample to an unconditional nearest-prototype limit and the near-tie abstention case both passed. These are implementation tests, not MNIST or Fashion-MNIST findings.

An independent mathematical workstream additionally checked its reference formulas over a larger synthetic corpus. The lead editor must reconcile the proof, recent literature gap and implementation before freezing the new protocol. No real-data fitting or held-out outcome analysis has been performed in this design workstream.

## Resource estimate

The original K=100 factorization phases took approximately 0.094–0.128 seconds each with 20,000 rows on this runtime. Scaling by N K² gives an engineering estimate of roughly 40–60 seconds for 210 endpoint factorizations; the full 480-factorization finite-probe audit is estimated at approximately 90–140 seconds, before distance construction, bound computations, query scoring and archival output. The actual run may take several minutes. This is a planning estimate, not a measured runtime result. K=200 float64 H uses 32 MB per seed/width; sequential processing avoids a large resident model grid. A full run should be bounded and checkpointed by dataset/seed; record actual runtime after execution.

## Status

Reserve indices and image provenance are audited. All four Fashion-MNIST creator files were acquired and passed the published MD5 checks; their contents were not decoded before protocol freeze. Dataset acquisition is read-only preparation. The proposed experiment is awaiting the lead editor's final theory/literature alignment and protocol freeze. No worker, model fit, hyperparameter selection or reserved-outcome evaluation was started.
