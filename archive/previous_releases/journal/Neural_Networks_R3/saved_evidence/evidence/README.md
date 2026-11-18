# Revised research evidence

This supplement preserves the complete original evidence and adds the
9 November 2026 guarded exclusion and local-tail analyses. Unzip it into an
empty folder; keep baseline/evidence and new_analysis in the supplied layout.

The exact protocols, input hashes, requirements, read-only verification and
full reproduction commands are in new_analysis/limit_diagnostic/README.md.
From this extracted root, the two primary checks are:

    PYTHONDONTWRITEBYTECODE=1 python baseline/evidence/baseline/verify_package.py --predictions
    PYTHONDONTWRITEBYTECODE=1 python new_analysis/limit_diagnostic/verify_diagnostic.py

The original checks reconstruct the archived study. The new analysis includes
120 fresh positive-ridge solves, 254,120 certified sampled decisions and zero
disagreements. The original complete training was not rerun during this revision.
The original frozen evidence records its earlier execution history.

verification/ contains independently written theorem and array checks and their
recorded outcomes. Running those scripts recomputes their adjacent JSON files.
build_new_material.py regenerates the new manuscript inputs and Figure 6 into
manuscript/; it requires Matplotlib in addition to the pinned analysis packages.
The original five figures are supplied unchanged in the manuscript source ZIP.

SHA256_MANIFEST.json covers every other entry in this supplement. The new
analysis retains its separate canonical manifest and baseline-input hashes.
The original archive's dataset provenance and licenses remain in baseline/evidence.
