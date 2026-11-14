# RBF research: preservation, insight extraction and review plan

14 November 2026 | Author: Meshaal Mouawad | Target: Neural Networks

## Decision and current status

Use the existing trained evidence as the primary research asset. Complete the bounded analyses below before deciding whether additional training is warranted. The next scientific revision is R4; R3 remains the preserved, verified baseline. R3 is technically complete. The additional scientific extension is not yet complete.

Default working model: **GPT-6.1 Sol, Medium reasoning**. Use High for numerical implementation or difficult debugging. Reserve **GPT-6 Astra, High** for one protocol/claim review and the final independent scientific review. Use GPT-6 Luna, Low for inventory, formatting and mechanical checks. These are task-specific recommendations, not measured cost estimates for this project. Model roles follow official guidance accessed 14 November 2026: https://developers.openai.com/api/docs/guides/model-selection . Actual account usage and API charges are different; no dollar budget or automatic model switching is asserted.

## 1. Data preservation: verified facts

Existing repository: https://github.com/Meshaal-Mouawad/Radial-Basis-Function-Neural-Network-for-MNIST-Digit-Classification

Audited original repository head: `1148fb8a81e634b288b5626dc8f4705d11ffff14`.

- All 30 `predictions_before_labels.npz` archives match the existing repository by SHA-256. These preserve fitted weights, predictions, prototype identities and splits across the original dataset/seed/prototype-budget groups.
- All 30 `frontiers_before_labels.npz` archives match GitHub by SHA-256.
- Original MNIST training and test MAT files match GitHub by SHA-256.
- Of the 446 files in the complete R2 evidence tree, 362 have exact byte matches in GitHub. The remaining 84 files occupy 192,130,025 bytes and belong to subsequent material or revised metadata. This is a file inventory, not a count of newly trained models.
- The complete R3 package is already saved: `RBF_Neural_Networks_Full_Revision_R3_2026-11-14.zip`, 419,266,881 bytes; SHA-256 `9c6a1769dc0f4c9392d93c12ee045531d70fffa36e5bdaa272da52de5870be7a`.
- That package contains the complete R2 research evidence and R3 numerical outputs, plus integrated LaTeX, PDF, protocols, numerical verifiers and original R2 sources. Fresh extraction and numerical reconstruction passed.


`evidence_inventory.json` gives the exact existing GitHub location or missing status for each file. Retain old paths and revisions. Never overwrite frozen evidence. Place subsequent work under `journal/Neural_Networks_R4/`. A public release of the complete binary supplement remains a separate synchronization step; the original training evidence is already on GitHub.

## 2. Additional analysis completed now

The supplied script reuses the 20 R3 endpoint settings and computes class-specific acceptance, correctness, selected-class macro accuracy, accepted recall, effective predicted-class count and selector overlap. No fitting or label-based selection was performed. Forty selector rows and 400 class rows passed count-identity checks.

| Dataset / width | Certificate accuracy | Equal-class selected accuracy | Gated-distance equal-class selected accuracy | Certificate/gated Jaccard |
|---|---:|---:|---:|---:|
| MNIST / sC/2 | 69.09% | 11.24% | 44.74% | 0.653 |
| MNIST / sC | 68.93% | 10.00% | 10.00% | 1.000 |
| Fashion-MNIST / sC/2 | 75.27% | 53.36% | 63.64% | 0.697 |
| Fashion-MNIST / sC | 64.65% | 25.49% | 44.21% | 0.313 |

Values are means across five seeds. Equal-class selected accuracy averages class-conditional accuracies among classes represented in the selected subset; counts of represented classes are saved. It evaluates correctness within the selected set. Macro accepted recall divides each class's selected correct count by its full evaluation count, treating unselected examples as unaccepted; it is a different metric.

At MNIST t=sC, the model predicts class 1 for every query and both selectors choose the same set in every seed. At Fashion-MNIST t=sC, the mean Jaccard of 0.313 shows substantially different selected sets at the same coverage. The effective number of predicted classes increases from 1.71 under certification to 3.73 under gated-distance selection. These are concrete next-revision insights, currently preserved as analysis outputs and not silently inserted into R3.

## 3. Bounded execution plan

Every stage produces machine-readable output, a brief interpretation and a PASS/FAIL/NOT-SUPPORTED status. Run scripts on saved arrays; language models write and inspect code rather than repeatedly calculating tables in chat. A null result closes a stage and remains in the record.

| Stage | Work and exact deliverable | Model / reasoning | Completion gate |
|---|---|---|---|
| A: preservation | Inventory, original GitHub matches, verified R3 archive and restore instructions | Luna / Low | Complete locally and in saved package; subsequent full binary GitHub synchronization recorded separately |
| B: protocol | Freeze analysis questions, endpoints, comparisons and interpretation rules below before new extraction | Sol / Medium; Astra / High once for design | Protocol JSON and claim-to-analysis matrix saved; no outcome-dependent changes |
| C: composition | Verify the new class-balanced metrics independently; generate per-class coverage/correctness and selector-overlap plots | Sol / Medium, High if a mismatch occurs | All 20 settings and 400 class rows agree; clearly distinguish selected accuracy from accepted recall |
| D: finite disagreement | Across the existing 96 readouts/group, locate smallest sampled penalty with strict disagreement, stable agreement, and any sampled reversals back; compare with sufficient bound B at matching widths | Sol / High | Per-query records distinguish observed grid brackets, censored cases and bound B; recover R3 masks exactly |
| E: useful operating region | Build accuracy/coverage/agreement/exclusion trade-off surfaces for all 30 original groups, including K=50 and K=200; separate near-optimal validation models from broad-width diagnostic endpoints | Sol / High | Every group included; validation-only selection with deterministic ties; evaluate retained models once; report all seeds and zero-coverage cases |
| F: exclusion efficiency | Order the existing finite probes by a prespecified width/penalty rule and compare cumulative exclusions with the analytical limit; count extra exclusions per probe and saved solve cost | Sol / Medium or High | Same requested regions and query IDs for each comparison; no best-order choice using evaluation labels; distinguish measured runtime from operation counts |
| G: stability | Use seed-paired differences, query-level overlap and class composition to identify repeatable findings; record shared evaluation images explicitly | Sol / High | Complete per-seed tables; no query-seed independence assumption; no inflated sample size from repeated probes |
| H: integrate R4 | Retain only supported findings in the main argument; place complete secondary results in supplement; update LaTeX, figures, abstract, cover letter and report | Sol / Medium; High for consistency audit | Compiled PDF inspected page by page; frozen equations/results/AI declaration preserved or corrections explicitly documented |
| I: independent review handoff | Freeze package; independent numerical rerun plus separate scientific assessment | Sol / High for independent numerics; Astra / High for scientific review | Readiness checklist below is all PASS; deliver one review ZIP and one-page decision summary |

## 4. Analysis specifications and stop rules

**D: disagreement threshold.** R3 establishes a sufficient bound. Extract empirical disagreement from the archived grid first. A first observed disagreement is not proof of a unique crossing. Save all sign changes, missing reference widths, strict-score guards and left/right-censored cases. Reconstruct only missing scores from saved weights; no refits. For an interval between sampled penalties, report a bracket rather than inventing the exact crossing. Any new continuous-path solver requires a separate prespecified method and verifier.

**E: competitive regimes and prototype budgets.** The original 30 groups include two datasets, five seeds and K=50/100/200. First audit which validation indices, weights and scores are available for every group. Reuse the R3 95%-of-best-validation rule as the primary descriptive threshold, with 90% and 99% fixed sensitivity analyses. Use validation data for model selection and all evaluation cases only for reporting. If certification has zero coverage across competitive readouts, report that result and close the practical-selection claim. Do not search indefinitely for a favorable width or seed.

**F: finite checking versus analytical exclusion.** Use both the original F0 and expanded F1 as in R3. Predeclare a fixed increasing-penalty order within widths and a fixed interleaving over widths. Record excluded-query counts after each probe, marginal unique exclusions, and overlap with L0/L+. A timing claim requires rerunning and timing only the relevant calculations with identical hardware, threads and warm-up rules; archived times from different environments are not directly comparable.

**G: statistical handling.** Give all five paired seed values and mean/SD. For exploratory intervals using evaluation resampling, resample common query IDs jointly across paired selectors and preserve dataset identity; interpret the result conditional on the existing trained models. Do not treat five seeds sharing images as five independent datasets. Avoid additional hypothesis tests unless a specific claim requires them; predefine a family and correction before testing.

**No automatic new-training stage.** The first objective is to exhaust the specified saved-data questions. New training is considered only if a named central question cannot be answered from stored models and a pilot specifies data, runs, compute, stopping condition and expected decision value. No paid compute is included in this plan.

## 5. Cost control

1. Use one Sol implementation session per coherent stage; resume from files, not a pasted entire conversation.
2. Pass the protocol, relevant script, schema and compact CSV summaries to the model. Keep raw arrays on disk.
3. Run a one-group timing pilot before expanding expensive score reconstruction. Log elapsed time and estimated remaining runtime; checkpoint each group. This provides a measured budget rather than a guessed wall-clock promise.
4. Retry a failed numerical stage once after diagnosing the error. Escalate the specific unresolved issue from Medium to High; use Astra only if the scientific or mathematical question remains unresolved. Do not run every stage with Max/Pro.
5. Rerun only analyses affected by a code change. Rebuild all tables once at final freeze. Keep cached distances, scores and eigendecompositions keyed by input hashes when useful.
6. The author can use Sol Medium for routine continuation and Astra High for the final independent review. The task's artifacts and acceptance tests determine completion, not model confidence or time spent.

## 6. Definition of complete for independent review

- [ ] Preservation inventory and restored numerical checks PASS; original GitHub evidence matches recorded.
- [ ] Stages C-G each have an outcome and complete outputs, including null outcomes; no required group silently omitted.
- [ ] Each central claim maps to a table/figure, script, CSV/array and exact input hashes.
- [ ] The distinction between sufficient reversal bounds and observed finite-grid disagreements is exact.
- [ ] The strongest selector baseline and class-composition findings appear in the manuscript.
- [ ] Every retained insight is independently recomputed from the preserved inputs.
- [ ] Integrated R4 LaTeX builds cleanly; every final PDF page is inspected; all references and numerical denominators reconcile.
- [ ] A clean extraction reproduces key tables; archive manifests verify; restore instructions are tested.
- [ ] `REVIEW_READY.json` records all gates PASS and names the frozen manuscript/evidence hashes. No marker is written while a required gate is unresolved.
- [ ] Independent reviewer receives the frozen manuscript, supplement, protocol, claim map, numerical verification and unresolved questions together.

After these gates, send the package for independent review even if the result narrows the contribution. Review readiness is an inspectable complete study; acceptance by Neural Networks is a separate editorial decision. The scientific reviewer should assess whether the continuous-region analysis establishes sufficient significance without being instructed to approve it.

## 7. Continuation instruction

Continue the RBF Neural Networks project from the verified R3 archive and this plan. Preserve R3 and all frozen evidence. Use the existing repository only. Complete stages B-I in order with checkpointed scripts and recorded gates; do not stop at prose suggestions. Start with saved-array analyses and no model retraining. Do not tune scientific thresholds to make results positive. Integrate supported findings into R4 LaTeX, compile and inspect the PDF, independently verify the numerical outputs, and produce a frozen review package. Record actual model/effort and runtime in the execution log. If external authentication blocks binary synchronization, preserve a verified upload-ready archive and label GitHub synchronization pending. Never claim remote preservation from a local file alone. Do not submit to a journal.

## Limitations and outstanding actions

The new composition diagnostics are verified by count identities and require a separate reconstruction before manuscript promotion. Stages B-I beyond those initial diagnostics are planned, not completed. The command-line GitHub client has no authenticated write session in this workspace; the connected GitHub tools can write the plan and text records. The later binary evidence is saved in the complete R3 backup and prepared for synchronization. Current public journal upload requirements remain to be checked before submission. No claim of exhaustive possible insights or guaranteed publication is made.