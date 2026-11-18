# Reproduce the guarded diagnostic and local-tail analysis

The primary results are the four directories `original7_guarded`, `dense67_guarded`, `local_tail`, and `local_tail_validation`. `FINAL_MANIFEST_SHA256.json` defines the exact canonical file set. The initial unguarded exploratory outputs are superseded and excluded from this supplement; the original protocol and subsequent finite-score amendment preserve their provenance.

## Required package layout

Run the commands below from the extracted package root, whose layout is:

```
baseline/evidence/baseline/repository/Code/MNIST_train.mat
baseline/evidence/baseline/work/v2/experiment/results/
baseline/evidence/baseline/work/v2/design/reserved_training_ids.npy
baseline/evidence/baseline/work/v2/data/fashion_mnist/
baseline/evidence/frontier/results/
new_analysis/limit_diagnostic/
```

The `baseline/evidence` directory is the complete preserved original evidence tree. Keep its nested `baseline` directory. Do not flatten or rename it. No download or network call is required. All scripts derive their root from their own location; there are no absolute filesystem paths.

`INPUT_SHA256.json` gives hashes for all 60 raw-data, indexed prediction/mask, label, choice, and CSV files read by the new diagnostic, validation, and count audit. The original evidence tree also supplies its original manifests and freeze receipts. The data are the original MNIST MATLAB file, the archived Fashion-MNIST IDX files, and the indexed splits/prototypes from the frozen study.

## Runtime

The recorded runtime is Python 3.12.14, NumPy 2.3.5, SciPy 1.17.0, and threadpoolctl 3.6.0 on Linux x86-64. `RUNTIME_VERSIONS.json` preserves the complete Python/platform string. The runners explicitly limit BLAS to one thread. Install the pinned analysis dependencies in your chosen environment with:

```bash
python -m pip install -r new_analysis/limit_diagnostic/requirements.txt
```

The original evidence verifier used below needs NumPy. Reproducing the original entire training pipeline is unnecessary for these analyses.

## Read-only verification of supplied results

From the package root:

```bash
PYTHONDONTWRITEBYTECODE=1 python baseline/evidence/baseline/verify_package.py --predictions
PYTHONDONTWRITEBYTECODE=1 python new_analysis/limit_diagnostic/verify_diagnostic.py
```

Expected original verifier outcome: `PASS`, 197 package-file hashes, 11 frozen inputs, 71 V2 result files, 45 prior-study files, 30 groups, 630 endpoint records, 1,890 certificate records, and 13,146,228 method-tagged finite checks with zero violations.

The new verifier checks the canonical manifest, all 60 baseline input hashes, stage manifests, strict-limit sign masks, certificate/exclusion disjointness, dense nesting, signed/simple correction ordering, positive interval-margin masks, and all 254,120 certified sampled decisions from the local-tail validation. Expected outcome: `PASS` and zero disagreements. These checks read supplied arrays and do not fit readouts.

## Full reproduction without overwriting supplied outputs

These POSIX shell commands create a separate result tree. Start with no existing `reproduced` directory. The symlink shares immutable baseline inputs with the supplied package. Only the four specified new analyses are recomputed.

```bash
mkdir -p reproduced/new_analysis/limit_diagnostic
ln -s ../baseline reproduced/baseline
cp new_analysis/limit_diagnostic/*.py reproduced/new_analysis/limit_diagnostic/
cp new_analysis/limit_diagnostic/protocol.json reproduced/new_analysis/limit_diagnostic/
cp new_analysis/limit_diagnostic/PROTOCOL_SHA256.txt reproduced/new_analysis/limit_diagnostic/
cp new_analysis/limit_diagnostic/finite_witness_amendment.json reproduced/new_analysis/limit_diagnostic/
cp new_analysis/limit_diagnostic/local_tail_protocol.json reproduced/new_analysis/limit_diagnostic/
cp new_analysis/limit_diagnostic/local_tail_validation_protocol.json reproduced/new_analysis/limit_diagnostic/

PYTHONDONTWRITEBYTECODE=1 python reproduced/new_analysis/limit_diagnostic/run_limit_diagnostic.py --guarded-finite
PYTHONDONTWRITEBYTECODE=1 python reproduced/new_analysis/limit_diagnostic/run_limit_diagnostic.py --dense --guarded-finite
PYTHONDONTWRITEBYTECODE=1 python reproduced/new_analysis/limit_diagnostic/run_local_tail.py
PYTHONDONTWRITEBYTECODE=1 python reproduced/new_analysis/limit_diagnostic/validate_local_tail.py
PYTHONDONTWRITEBYTECODE=1 python reproduced/new_analysis/limit_diagnostic/audit_and_summarize.py
PYTHONDONTWRITEBYTECODE=1 python new_analysis/limit_diagnostic/verify_diagnostic.py --compare-reproduction reproduced/new_analysis/limit_diagnostic
```

The first two commands compute numerical obstructions using existing weights, original image geometry, and recomputed class-response sums. The third computes local-band thresholds without fitting a readout. The fourth performs 120 new positive-ridge solves for numerical validation. The fifth rebuilds count-audit and frontier-summary files. The final command compares every scientific NPZ array and every stage CSV exactly, then compares the manuscript count audit. Archive ZIP bytes, new timestamps, elapsed times, and runtime receipts are not treated as scientific-array equality. Exact comparisons target the pinned runtime; different BLAS or library builds can change floating-point entries.

## Expected scientific outcomes and measurement units

- Ten dataset/seed groups, all at `K=100`; five seeds per dataset.
- Original guarded grid: 210 width/floor/group records, 490,945 query/width cases before floor repetition.
- Dense guarded grid: 2,010 width/floor/group records, 4,699,045 query/width cases before floor repetition.
- At the first dense width with zero certification for each seed and floor zero: mean exclusion 0.377452% MNIST and 0.438000% Fashion-MNIST; unresolved 99.622548% and 99.562000%.
- At original `t=s_C`, floor zero: combined exclusion 88.095356% MNIST and 84.480000% Fashion-MNIST.
- Local study: 40 bands; 80 method-tagged records, preserving the positive-sum comparator and the sharper signed-interval correction.
- Local validation: 120 readouts, 254,120 certified query-parameter checks, zero disagreements.
- Original manuscript count audit: 5,289,327 sharp finite checks; 13,146,228 method-tagged finite checks; 3,585,477 within-group deduplicated query/parameter checks; 35 dense sharp/basic gain conditions and 827 repeated query-condition gains.

Each complete-set percentage uses 4,027 MNIST queries or 10,000 Fashion-MNIST queries within a seed. Summaries are unweighted five-seed means with sample SD in percentage points. The same images are reused across seeds and settings. The three categories are the original sharp-certified mask, the union of strict guarded limiting/finite witnesses, and the unresolved remainder. Ties and cases without a witness remain unresolved.

The limiting scaled score uses `Z_sigma=H_sigma^T Y`. Existing array keys remain `HtY` in diagnostic archives and `B_s,B_t` in local archives for source compatibility. Query features are max-normalized by subtracting the nearest squared distance before exponentiation. Raw ridge penalties belong to the original unnormalized sum-of-squares objective; normalized thresholds divide by `||H_t^T H_t||_2`.

## Comparator and numerical validation

At penalty `10||H_t^T H_t||_2`, complete-query coverage means are:

| Dataset | Upper width | Band | Positive-sum % | Signed interval % |
|---|---:|---:|---:|---:|
| MNIST | `0.5s_C` | 1% | 16.7867 | 16.8761 |
| MNIST | `0.5s_C` | 5% | 16.6576 | 16.7718 |
| MNIST | `s_C` | 1% | 2.3442 | 16.7867 |
| MNIST | `s_C` | 5% | 0 | 16.7817 |
| Fashion-MNIST | `0.5s_C` | 1% | 23.9360 | 40.0920 |
| Fashion-MNIST | `0.5s_C` | 5% | 9.6920 | 22.1520 |
| Fashion-MNIST | `s_C` | 1% | 0 | 14.9380 |
| Fashion-MNIST | `s_C` | 5% | 0 | 0 |

`local_tail_validation/all_query_summary.csv` reports all-query accuracy and nearest-label agreement at both numerical penalties. `certified_summary.csv` separately reports subset correctness, zero-coverage seeds, and disagreements. The measured all-query accuracy at penalty multiple 10 is 15.5997% and 11.7705% for MNIST upper widths `0.5s_C,s_C`, and 45.0600% and 29.8580% for Fashion-MNIST. The local-tail result establishes a guarantee for a different parameter family; it does not establish a higher-accuracy operating range.

## Provenance, timing, and interpretation

All new protocols are explicitly post hoc. `protocol.json` precedes the staged calculation; `finite_witness_amendment.json` precedes score-guarded recalculation; the local-bound and numerical-validation protocols precede their respective computations. The original source and original evidence are preserved. Scientific reviewer notes explain the strict limiting-score implication and local resolvent theorem. Numerical signs use float64 guards, without outward-rounded arithmetic.

Recorded elapsed times are 4.9023 s for the guarded original-grid diagnostic, 27.2744 s for the guarded dense-grid diagnostic, 10.9215 s for the fit-free local-bound computation, and 2.6607 s for the 120-readout validation and scoring. These are environment-specific elapsed times, not speedup benchmarks. `COMPLETE.json` files retain exact timings and group receipts.

Only the canonical files listed in `FINAL_MANIFEST_SHA256.json` belong in the primary new-analysis supplement. Their disk footprint is recorded in `PACKAGE_FOOTPRINT.json`; source inputs in the preserved baseline tree are additional. The superseded unguarded outputs and interpreter caches are excluded.
