# Supplementary post hoc bandwidth frontier analysis

`REPORT.md` reports the completed M1 analysis. `protocol.json` specifies the label-free width grid and endpoint choices. `FREEZE.json` hashes that protocol, the runner, unchanged archived certificate and 41 input files before the successful run. The complete first aborted attempt is retained separately.

All paths are relative to this directory. The expected package structure is sibling directories `baseline/` and `frontier/`; no absolute workspace path is required. The original baseline is preserved: `BASELINE_INTEGRITY.json` verifies all 262 baseline manifest entries and records zero changed or additional files. `RUNTIME_VERSIONS.json` gives the package versions; `results/environment.json` gives Python/platform/BLAS information. The runner applies `threadpool_limits(1)` to the whole computation.

To repeat in a copied package, first rename the existing `frontier/results/` directory to retain the archived outputs. The runner deliberately refuses to overwrite an existing output directory. From the package root run:

```sh
PYTHONDONTWRITEBYTECODE=1 python -u frontier/run_frontier.py
PYTHONDONTWRITEBYTECODE=1 python frontier/analyze_frontier.py
```

The run needs the archived images and indices under `baseline/`. It verifies the input and source hashes before computing. Evaluation targets are accessed only after all supplementary predictions, weights, masks and selected endpoint indices have been saved and hashed. The separate report generator summarizes those fixed records and has no role in fitting or endpoint selection.

`results/MANIFEST_SHA256.json` is the runner-generated hash manifest before descriptive report summaries were added. `ARTIFACT_MANIFEST_SHA256.json` is the final complete supplementary file manifest. Timestamp metadata and compressed archive metadata may change on rerun; compare arrays, coverage counts and readout labels as the scientific records.

Every per-group `frontiers_before_labels.npz` stores masks in `(width, floor, method, query)` order, last passing/next failing indices in `(floor, method, query)` order, all frozen indices, pair constants, selected endpoint SVD weights and predictions. Method order is sharp, basic, cancellation_frobenius; floor order is 0, 1, 100. A last passing index of -1 is left censoring; a next failing index of -1 is right censoring. The `chosen_endpoints_before_labels.json` files map coverage targets to grid indices. All 270 endpoint target conditions are available in the successful run.

The final grid has 67 widths from `s_C/32` to `s_C/4`, exactly including `s_C/16`, `s_C/8` and `s_C/4`; adjacent widths differ by `2^(1/22)`. Original shared-width masks match exactly, numerical nesting and method hierarchy checks pass, and certified endpoint disagreements are zero.
