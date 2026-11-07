# Supplementary Research Artifacts

Training-Derived Regions of Nearest-Prototype Agreement in Gaussian RBF Classifiers

The baseline/ folder preserves the executed experiments, source, indexed splits, original images and provenance, saved readouts/predictions/masks, all declared conditions and scientific checks. Its outer manifest indexes the scientific submission subset. The frozen source/input/result identities are unchanged.
The frontier/ folder preserves the separately declared 67-width post hoc analysis, masks, per-query brackets, endpoint predictions, freeze receipts, source and reports. Reproduction/ contains the independent reconstruction evidence and fresh-execution comparison record. The complete raw original experiment is included; the additional fresh-run duplicate arrays are reproducible using the unchanged runner and retained execution log.

## Verify without fitting

From this extracted root run:

    python baseline/verify_package.py --predictions

Dependencies: NumPy; full pinned fitting requirements are baseline/work/v2/experiment/requirements.txt. The command is read-only and reconstructs all 630 endpoints,1,890 certificate rows and13,146,228 finite certified checks. The theorem establishes the continuous guarantee.

## Independent re-analysis and fresh execution

Use a separate working copy for commands writing new audit outputs:

    PYTHONDONTWRITEBYTECODE=1 python reproduction/independent_audit.py --baseline baseline --output audit_new
    PYTHONDONTWRITEBYTECODE=1 python theory/audit_frontier_results.py

For a fresh full fit choose a new empty output directory:

    PYTHONDONTWRITEBYTECODE=1 python baseline/work/v2/experiment/run_experiment.py --protocol baseline/work/v2/experiment/protocol.json --freeze baseline/work/v2/experiment/FREEZE.json --output-dir rerun/results --execute

Then add --fresh-results rerun/results to the independent_audit.py command to compare newly fitted arrays. The runner refuses nonempty outputs. frontier/README.md specifies supplementary rerun and archive schemas.

The preserved reproduction report describes the original author archive with262file checks and its fresh run; this submission subset has its own manifest count. Historical absolute execution paths identify the recorded runtime only; commands above and the scripts resolve relative package paths. Dataset licenses and canonical provenance are included.
