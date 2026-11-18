# Fresh executable audit of the R4 scientific supplement

**PASS.** The package integrity check and all four unchanged independent numerical verifiers completed successfully. Fresh receipts reproduce every original scientific field. The three core receipts differ only in measured runtime; the final-table receipt is byte-identical to its delivered original.

## Executions

Commands ran from the supplement root with `OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 PYTHONDONTWRITEBYTECODE=1`. The composition run was the timing pilot; all remaining runs were tractable and completed sequentially. NumPy 2.3.5 and SciPy 1.17.0 match the supplied README. All five return codes were zero.

| Script | Outcome | Wall seconds | Internal seconds |
|---|---|---:|---:|
| `verify_package.py` | PASS | 0.526896 | not emitted |
| `verify_composition.py` | PASS | 2.050295 | 1.7422821720000456 |
| `verify_competitive.py` | PASS | 46.140149 | 45.83139671599997 |
| `verify_paths_efficiency.py` | PASS | 22.573759 | 22.262123504999977 |
| `verify_summary_tables.py` | PASS | 0.590312 | not emitted |

## Reconstructed evidence

| Verification | Freshly reproduced counts and findings |
|---|---|
| Composition | 140,270 endpoint labels; 20 settings; 40 selector rows; 400 class rows; eight summaries. All metrics, class counts, means and sample SDs match. At MNIST t=s_C every endpoint prediction is class 1 and the two selectors select identical subsets. |
| Competitive regions and stability | 30 groups; 14,400,000 validation labels; 20,198,880 evaluation labels; 2,880 independently coded sharp masks; all 630 original masks; 2,880 surface rows; 90 threshold rows; 300 class rows; 30 budget comparisons; 60 cross-seed comparisons. |
| Sampled paths and probe accumulation | 20,198,880 predictions; 3,366,480 query-width paths; 480 path summary rows; 70 bound comparisons; 1,161 finite-probe masks; 21,630 cumulative-probe rows; 420 efficiency regions. Original and expanded R3 unions match exactly. |
| Final tables | Six validation-best summaries; 18 competitive summaries; six paired-budget summaries. The 90%, 95% and 99% thresholds retain 494, 328 and 116 models. Every threshold has zero certificate coverage in all 30 groups. |
| Path findings | 190,405 query-width cases return from strict disagreement to strict agreement; maximum five strict sign changes across the six sampled penalties; zero guard or rank-invalid cases. |

## Integrity and preservation

The initial integrity check verified 774 manifest-listed files in 0.526896 seconds. The final integrity check verified the same 774 files in 0.461279 seconds. The root manifest SHA-256 is `f5722995db5788574eda29a1f84e85735b9562b2ab4b61f67f6558efef9abe75`. This hash identifies the extracted supplement manifest.

**finaloriginalbytes: PASS.** All 775 extracted files, including the manifest itself, match their baseline SHA-256 values after execution. There are zero added, deleted or changed files in the supplement. The eight delivered adjacent JSON/log records were preserved before rerunning. Fresh receipts and logs are retained in this audit directory; the delivered originals were restored in the supplement.

The initial/final manifest checks establish delivered-byte integrity. The four fresh runs establish numerical reconstruction of archived predictions, certificate masks, states, accumulations and descriptive summaries from the supplied data and fitted weights.

## Exact records

`EXECUTABLE_AUDIT.json` retains execution return codes, wall and emitted internal runtimes, verifier source hashes, environment, counts and the final preservation verdict. `verifier_scientific_input_sha256.json` enumerates the scientific files read by each unchanged verifier: 38 composition inputs, 72 competitive inputs, 186 path/efficiency inputs and 148 final-table inputs. The summary script's three fresh core-receipt dependencies have separate hashes in `summary_fresh_receipt_dependencies_sha256.json`. `baseline_tree_sha256.json` contains hashes for every extracted file. Original and fresh receipt hashes and changed fields are recorded in `fresh_vs_original_receipts.json`.

## Limitations

These executions use the archived fitted weights and perform zero new fits or training. Prediction and query-width reconstruction counts reuse the supplied 4,027 MNIST and 10,000 Fashion-MNIST evaluation images across seeds and parameter conditions. The supplied verifiers do not execute the independent reviewer's 90 synthetic geometries; this audit claims no such experiment.
