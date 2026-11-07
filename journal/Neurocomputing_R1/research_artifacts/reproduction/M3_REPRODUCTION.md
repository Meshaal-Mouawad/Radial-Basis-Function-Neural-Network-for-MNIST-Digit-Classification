# M3: independent archive reconstruction and fresh training reproduction

**M3 is closed.** All 18 rows of manuscript Table 2 reproduce to the printed precision from the recovered v3 archive. Independent code reconstructs all 1,890 certificate masks from the original images and training labels, reproduces all 630 endpoint scoring records, and finds zero finite-probe violations. A fresh execution of the complete frozen experiment reproduces the scientific arrays and all endpoint/certificate CSV results across all 30 groups.

Date: 7 November 2026. Preserved input: `../baseline/`. Nothing in that tree was edited. The final preservation check again passed every package, experiment and earlier-study manifest entry. The review's M3 request was read in `../review/Gold_Niche_Review_RBF_MNIST_v2.md`; the tested claims were read in `../baseline/manuscript/results.tex` and the archived protocol and evidence documentation.

## Executed evidence levels

| Operation | Inputs and execution | Result |
|---|---|---|
| Independent reconstruction | `independent_audit.py`, written for this audit; imports no archived runner, certificate, verifier or prior analysis code | Original images/labels → distances → training terms → pair constants → masks; original labels plus stored predictions → all scoring records |
| Stored-weight prediction reconstruction | Independently rebuilt normalized query features multiplied by every stored weight matrix | 20,198,880 prediction labels, zero mismatches |
| Fresh full training | Unchanged frozen `run_experiment.py`, new `fresh_results/` directory | 480 SVD factorizations, 2,880 fitted readouts, 30 groups; complete success |
| Fresh-versus-original comparison | Every scientific NPZ array, excluding timing arrays, and all scientific CSV fields | Discrete arrays identical; finite floating values have maximum observed absolute difference 0; 630 endpoint and 1,890 certificate CSV rows agree exactly |
| Supplied archive verifier | `verify_package.py --predictions` | PASS, including 13,146,228 certified finite checks |

The fresh execution's `COMPLETE.json` records **116.2922 s** for the main computation; the original records **123.2019 s**. The final runner log includes extra manifest-writing time and prints 116.3865 s. These are separate execution records, not a repeated performance estimate.

## Reconstructed counts

| Quantity | Independent result |
|---|---:|
| Dataset–seed–budget groups | 30 |
| Endpoint / certificate records | 630 / 1,890 |
| Query–region cases | 4,418,505 |
| Inapplicable regions, retained in denominator | 102 |
| Sharp / basic certified query–region cases | 587,703 / 587,703 |
| Frobenius certified query–region cases | 285,286 |
| Sharp finite-probe comparisons | 5,289,327 |
| All methods, method-tagged comparisons | 13,146,228 |
| Deduplicated query–parameter comparisons | 3,585,477 |
| Certified finite-probe violations | 0 |

Sharp and basic masks are identical for every archived query and region. Frobenius masks are contained in them. Every method has zero coverage at every endpoint other than `s_C/16`. All selected prototype images are distinct within each group. All archived numerical ranks are full under the frozen cutoff. The smallest reconstructed certified raw margin is **1.4658047523430362 × 10⁻⁵**, and its minimum margin-to-guard ratio is **51,145.067211842426**.

## Table 2 reconstructed independently

Means are percentages; standard deviations are sample standard deviations in percentage points over five seeds. The two zero counts are sharp/Frobenius. All 18 rows match `manuscript/results.tex` to its two-decimal precision and exactly for zero-seed counts.

| Dataset | K | Floor | Sharp / basic | Frobenius | Zero seeds |
|---|---:|---:|---:|---:|---:|
| MNIST | 50 | 0 | 99.94 ± 0.04 | 78.29 ± 43.79 | 0 / 1 |
| MNIST | 50 | 1 | 99.94 ± 0.04 | 78.29 ± 43.79 | 0 / 1 |
| MNIST | 50 | 100 | 99.94 ± 0.04 | 78.29 ± 43.79 | 0 / 1 |
| MNIST | 100 | 0 | 99.91 ± 0.06 | 58.68 ± 53.57 | 0 / 2 |
| MNIST | 100 | 1 | 99.91 ± 0.06 | 58.68 ± 53.57 | 0 / 2 |
| MNIST | 100 | 100 | 99.91 ± 0.06 | 58.68 ± 53.57 | 0 / 2 |
| MNIST | 200 | 0 | 99.86 ± 0.03 | 0.00 ± 0.00 | 0 / 5 |
| MNIST | 200 | 1 | 99.86 ± 0.03 | 0.00 ± 0.00 | 0 / 5 |
| MNIST | 200 | 100 | 99.87 ± 0.03 | 0.00 ± 0.00 | 0 / 5 |
| Fashion-MNIST | 50 | 0 | 99.33 ± 1.35 | 58.93 ± 53.83 | 0 / 2 |
| Fashion-MNIST | 50 | 1 | 99.71 ± 0.48 | 58.93 ± 53.83 | 0 / 2 |
| Fashion-MNIST | 50 | 100 | 99.77 ± 0.35 | 58.93 ± 53.83 | 0 / 2 |
| Fashion-MNIST | 100 | 0 | 79.09 ± 44.25 | 39.31 ± 53.83 | 1 / 3 |
| Fashion-MNIST | 100 | 1 | 79.63 ± 44.52 | 39.31 ± 53.83 | 1 / 3 |
| Fashion-MNIST | 100 | 100 | 98.66 ± 2.22 | 39.31 ± 53.83 | 0 / 3 |
| Fashion-MNIST | 200 | 0 | 79.06 ± 44.23 | 36.77 ± 50.52 | 1 / 3 |
| Fashion-MNIST | 200 | 1 | 79.54 ± 44.47 | 36.79 ± 50.54 | 1 / 3 |
| Fashion-MNIST | 200 | 100 | 98.54 ± 2.26 | 36.80 ± 50.55 | 0 / 3 |

## Accuracy claims and complete records

For `K=100`, zero penalty, readout accuracy at `s_C/16` and `s_C` reproduces as **70.55 ± 2.57% → 88.31 ± 0.19%** on MNIST and **63.30 ± 3.22% → 79.29 ± 0.64%** on Fashion-MNIST. Nearest-prototype accuracy reproduces as **70.52 ± 2.58%** and **63.29 ± 3.23%**, respectively. At `s_C`, nearest-prototype/readout agreement reproduces as **73.49 ± 2.42%** and **68.82 ± 3.74%**. The absolute-width-one agreement reproduces as **97.82%** and **98.27%**.

`independent_endpoints.csv` contains all 630 per-seed endpoint records, and `aggregate_endpoint_accuracy.csv` contains all 126 dataset/budget/width/floor summaries with five-seed means and sample standard deviations for every scored endpoint metric. `independent_coverage.csv` contains all 1,890 per-seed certificate records; `aggregate_coverage.csv` contains all 378 corresponding five-seed summaries. `table2_reconstructed.csv` contains unrounded Table 2 statistics. `independent_groups.csv` records each group's scale, baseline accuracy, index sizes and check counts.

## Integrity, indices, provenance and chronology

All **262 package file hashes**, **71 frozen result hashes**, **45 earlier-study hashes**, and **11 protocol-input hashes** match. All four directly checked source/protocol/synthetic freeze hashes match. The archived independent theory review also matches its frozen SHA-256 `0cac62664d65076ba3b2f0330c7883984e194a37b14be9cf4f2a71474305bfc9`.

The authoritative frozen SHA-256 identities are:

| File | SHA-256 |
|---|---|
| `protocol.json` | `63aa7750d07f2bc74e46e01cf7b1866f487504f64ff325ff94135f122bca36d5` |
| `run_experiment.py` | `52e60a9221a6610e2c68c64d06f5781489267dd9852fdc858abdda9796f10065` |
| `certificate.py` | `97e4890a185573bed1ff2229cccbcb476e0eb9036084b4807c37e885e3428603` |
| `synthetic_checks.json` | `364efd5f480d1e4c16e1e17645ba69440b4f5a943d1739f4bc8d54e02ba41bc5` |

Every MNIST training and test image and label in the supplied MAT arrays matches the archived canonical IDX payload at the same index. The 4,027 reserve IDs exactly equal the complement of the 55,973-image union of earlier train/validation IDs. Every MNIST group excludes the entire reserve from both training and validation. Every group has disjoint 20,000-row training and 5,000-row validation sets; each center index equals the indexed training row and its label matches the original training labels. MNIST preserves the earlier 100 centers, uses their first 50, and appends the specified seeded 100; Fashion-MNIST reproduces both stratified splits and the seeded 200-center draw. All budgets reproduce the declared prefixes. Fashion query IDs index its separate 10,000-row official test array.

All 30 prediction-freeze receipts match the NPZ hashes and the aggregate freeze list. Their recorded times lie after protocol freezing and no later than `ALL_PREDICTIONS_FROZEN.json`; that record precedes final scoring completion. Inspection of the unchanged runner confirms that all groups are generated before its label-scoring phase. The full MNIST label array is loaded for training; reserve entries are excluded from fitting and selection by the checked indices. The fresh execution follows the same sequence.

## Environment and exact commands

Both the archived and current environments use Python **3.12.14**, NumPy **2.3.5**, SciPy **1.17.0**, scikit-learn **1.8.0**, and threadpoolctl **3.6.0**. The runner enters `threadpool_limits(1)` for its main computation. Its environment JSON captures thread-pool metadata before entering that context. The exact core dependency file is `../baseline/work/v2/experiment/requirements.txt`.

From the v4 directory, the commands executed were:

```bash
python baseline/verify_package.py --predictions > reproduction/supplied_verifier.json

python baseline/work/v2/experiment/run_experiment.py \
  --protocol baseline/work/v2/experiment/protocol.json \
  --freeze baseline/work/v2/experiment/FREEZE.json \
  --output-dir reproduction/fresh_results --execute \
  > reproduction/fresh_run.log 2>&1

python reproduction/independent_audit.py \
  --fresh-results reproduction/fresh_results \
  > reproduction/independent_audit.log 2>&1

python reproduction/summarize_reconstruction.py \
  > reproduction/reconstruction_summary.log 2>&1

python baseline/verify_package.py > reproduction/preservation_after.json
```

For another fresh training execution, choose a new empty output directory; the frozen runner rejects nonempty outputs. The independent audit can be repeated against the already completed `fresh_results/` directory. The evidence directory contains both scripts, their JSON/CSV results, both verifier receipts, the run log and all fresh model outputs.

## Limitations

The independent implementation reconstructs certificate computations and scoring; the new training fits execute the original frozen runner. Floating comparisons use `rtol=2e-12, atol=2e-12`; independently recomputed pair constants differ by at most `5.96 × 10⁻⁸` in absolute value on large constants because of equivalent norm summation, with every mask identical. V/P/Q, beta and mu reconstruct exactly; fresh-runner scientific floating arrays match the original with zero observed finite difference. Timing fields and archive byte hashes change between executions. Freeze timestamps establish consistency of the supplied records; historical execution time is not independently observed. Finite probe checks test the recorded numerical predictions; the continuous-region guarantee rests on the theorem. The repeated query/parameter checks are repeated uses of the same evaluation images.
