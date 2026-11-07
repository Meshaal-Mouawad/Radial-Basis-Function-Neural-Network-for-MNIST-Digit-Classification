# Controlled RBF MNIST study

This directory contains a completed new experiment performed on 6 November 2026. It preserves and does not overwrite the 10 April 2026 source study.

- `protocol.json` and `protocol.sha256`: design frozen before the experiment.
- `run_study.py`: unchanged executed source. Its hash is in `results/environment.json` and `results/COMPLETE.json`.
- `results/`: 140 validation fits, 30 test records, 35 matched RLS/ridge comparisons, five prediction archives with split and prototype indices, and runtime/checksum records.
- `archive_equivalence_weights.py`: separately executed artifact reconstruction using saved indices. It introduces no new setting or model selection and checks its recalculated scalar metrics against the original records.
- `results/equivalence_weights/`: both fitted coefficient matrices and both test-label arrays for all 35 comparisons, with `AUDIT.json` recording the auxiliary source hash and verification.
- `analyze_results.py`: descriptive summaries and publication figures, with no model fitting.
- `figures/`: editable vector PDF and SVG exports plus inspected PNG previews.
- `EVIDENCE_REPORT.md`: design, measured results, interpretation, and evidence boundaries.
- `MANIFEST_SHA256.json`: hashes of the completed directory, excluding this manifest and Python bytecode caches.

Reproduction from the repository root:

```bash
python work/controlled_study/run_study.py --data-dir repository/Code --output-dir <new-output-directory>
```

The script validates the two supplied MAT file hashes. Do not overwrite the recorded result directory with a rerun. `requirements.txt` records the package versions used. The original source run and result hashes remain unchanged after the separate weight archive addition.
