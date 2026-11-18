# Uniform nearest-prototype label-agreement study

The prospective experiment is completed. Begin with `EVIDENCE_REPORT.md`, `FREEZE.json`, and `execution_verification.json`.

- `protocol.json`: authoritative frozen design.
- `certificate.py`: executed sharp, basic and cancellation-aware Frobenius conditions.
- `run_experiment.py`: executed data, fitting, prediction and scoring procedure.
- `results/`: immutable completed predictions, fitted weights, certificate masks, comparison tables and checksum manifest.
- `run.log`: attached execution output, including every completed group and final completion.
- `synthetic_checks.json`: pre-execution implementation checks, including duplicate and tie cases.
- `protocol_draft.json`: superseded pre-freeze working proposal, retained outside the authoritative result manifest.
- `analyze_experiment.py`: optional descriptive-analysis helper written after execution began; it is not part of the fitting source hash and was not run by the experiment workstream. The independent analysis workstream owns `work/v2/analysis/`.

All 30 prediction groups were frozen before evaluation targets were used for scoring. The current study is separate from the earlier RBF/MNIST evaluation and from the original April 10 research report. Reproduction commands and directory requirements are in `EVIDENCE_REPORT.md`.
