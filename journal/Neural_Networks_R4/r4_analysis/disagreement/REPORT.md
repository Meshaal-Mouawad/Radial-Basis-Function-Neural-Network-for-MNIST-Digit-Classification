# R4 stages D and F: finite paths and exclusion accumulation

Both stages are complete for their prespecified groups. Stage D covers all 30 original dataset/seed/prototype-budget groups and all 96 archived readouts per group. Stage F uses the ten K=100 groups and exactly the seven widths and three penalty floors compared in R3. No new model was fitted. All 20,198,880 original query predictions were reconstructed exactly. Grouped numerical runtime was 40.52 seconds, including output writing; this is analysis runtime, not an analytical-versus-finite speed comparison.

## D: sampled disagreement is nonmonotone in penalty

For each query and width, the saved margin is the highest competing class score minus the nearest-prototype class score. The numerical guard is `1e-10*(1+abs(competing)+abs(nearest))`. A positive margin beyond the guard is strict disagreement; a negative margin beyond the guard is strict agreement. Every one of the 20,198,880 observed margins was outside the guard. All archived zero-penalty fits met their numerical full-rank condition.

The six sampled penalties are 0, 1, 10, 100, 1,000 and 10,000. First disagreement at penalty zero is recorded as initial/left-censored disagreement. A first disagreement after zero has an adjacent strict-agreement/strict-disagreement bracket. No-disagreement cases are recorded through the maximum sampled penalty. All states and every sign change remain recoverable in the per-query arrays.

The following percentages are means across five seeds. A path is one evaluation query at one of the 16 archived widths. Each MNIST seed contributes 64,432 paths and each Fashion-MNIST seed contributes 160,000 paths.

| Dataset | K | Any sampled disagreement (%) | Initial disagreement at zero (%) | First disagreement after zero (%) | Strict agreement at every sample (%) | Sampled return to agreement, mean ± SD (%) |
|---|---:|---:|---:|---:|---:|---:|
| MNIST | 50 | 31.20 | 13.74 | 17.47 | 68.80 | 6.02 ± 0.94 |
| MNIST | 100 | 27.73 | 11.18 | 16.55 | 72.27 | 4.87 ± 0.65 |
| MNIST | 200 | 25.16 | 8.81 | 16.34 | 74.84 | 4.02 ± 0.44 |
| Fashion-MNIST | 50 | 25.36 | 15.46 | 9.90 | 74.64 | 6.40 ± 1.59 |
| Fashion-MNIST | 100 | 24.85 | 13.74 | 11.10 | 75.15 | 6.01 ± 0.95 |
| Fashion-MNIST | 200 | 23.45 | 12.06 | 11.40 | 76.55 | 5.39 ± 0.58 |

A total of 190,405 query-width paths return to strict agreement after an earlier sampled disagreement, among 3,366,480 audit paths. The largest observed number of strict sign changes is five over the six sampled penalties. One explicit K=100 example is Fashion-MNIST seed 22, width index 14 (`1.5s_C`), query ID 50: the strict states alternate agreement/disagreement at every sampled penalty. The six raw margins are approximately -0.017925, 0.040578, -0.033922, 0.009067, -0.017918 and 0.011859; their guards are approximately 1.4e-10 to 1.9e-10. This example is a transparent illustration selected after the exhaustive path analysis; the table reports the full prespecified grid.

### Observed finite disagreements versus the sufficient bound B

Bound comparisons use K=100 at the seven matching R3 widths only. The other nine original probe widths and every K=50/K=200 width are explicitly marked as lacking an archived bound reference. A finite B means the R3 strict limiting-reversal condition passed; infinite B means it did not pass. These statuses are distinct from missing bound references.

At `t=s_C`, all 16,755 finite MNIST bounds and all 33,135 finite Fashion-MNIST bounds exceed the original maximum sampled penalty of 10,000. In those same cases, 9,714 MNIST and 19,154 Fashion-MNIST query-width records already show a sampled disagreement below B. A further 878 MNIST and 8,808 Fashion-MNIST records show finite-grid disagreement without a finite strict-limit bound at that endpoint. The results separate a sufficient guarantee for the penalty tail from finite disagreement within the sampled path.

At `t=s_C/2`, the sampled grid contains 10,335 MNIST and 5,728 Fashion-MNIST query–penalty pairs above their sufficient bounds. Every corresponding raw competing margin is positive. All bound comparisons and ratio denominators are retained in `results/D_bounds.csv`; the raw per-query records include bound widths, operator norms and B itself.

## F: fixed-order finite exclusion accumulation

F0 comprises the 96 original readouts per group. F1 adds all archived frontier and local-tail readouts, exactly as in R3. For each requested region, the order first filters included widths and penalties. Widths are sorted ascending. Within each width, penalties are sorted ascending, with a fixed source tie-break. Probes then interleave round-robin over widths: first eligible penalty for each width, then second, and so on. This order was recorded before extraction.

Every cumulative step stores its marginal new exclusions, cumulative finite set size, overlap with L0 and L+, and both augmented unions. L0 is the R3 original-width limiting union; L+ also includes the dense-grid limiting witnesses. Final F0 and F1 masks match every R3 requested-region mask exactly.

At penalty floor zero and upper width `t=s_C`:

| Dataset | Probe set | Eligible archived checks, mean | Seeds reaching 95% of L0 cases | Checks to reach 95% of L0, mean | Seeds recovering every L0 case | Checks recovering all L0, mean | L0 cases still unique at the end (%) |
|---|---|---:|---:|---:|---:|---:|---:|
| MNIST | F0 | 84.0 | 0/5 | — | 0/5 | — | 8.026 |
| MNIST | F1 | 100.8 | 5/5 | 15.6 | 5/5 | 17.6 | 0.000 |
| Fashion-MNIST | F0 | 84.0 | 0/5 | — | 0/5 | — | 21.458 |
| Fashion-MNIST | F1 | 107.4 | 5/5 | 20.2 | 0/5 | — | 0.134 |

The F1 order includes archived high-penalty local-tail probes when their widths become eligible. Its earlier recovery of L0 cases reflects both that expanded probe support and the recorded ordering. Complete results for all seven widths and all three floors appear in `F_summary.csv` and `F_aggregate.csv`; the per-group `F_steps.csv` files preserve every probe and marginal increment.

The operation-count record also identifies the earliest prefix recovering each final finite or analytically augmented exclusion union. For example, at `t=s_C`, the final F1 finite union is recovered after mean 49.6 MNIST checks and 107.4 Fashion-MNIST checks. Those prefix counts are retrospective set-completeness measurements. The actual number of new factorizations and readout solves is zero throughout this analysis because all weights are archived.

## Files and verification

- `protocol.json`: pre-extraction specification; SHA-256 `53f0e8b55140eb90bcfae9901bac1540bc46a34a3698d38d02fdc7bbe5e72038`.
- `run_saved_paths.py`: executable stages D/F with `--pilot` and `--recompute` options.
- `PILOT.json`: measured one-group pilot and planning estimate.
- `results/D_per_width.csv`: all 480 dataset/seed/K/width rows.
- `results/D_per_group.csv`: all 30 groups and their exact audit denominators.
- `results/D_summary.csv`: six dataset/K summaries with seed mean and sample SD.
- `results/D_bounds.csv`: 70 matching K=100 width rows with B comparisons and censoring counts.
- `results/*_paths.npz`: raw margins, guards, strict states, first-detection brackets, sign changes, returns, query IDs and available bounds.
- `results/F_summary.csv`: all 420 dataset/seed/region/probe-set rows.
- `results/F_aggregate.csv`: five-seed summaries of fixed-order probe counts and exclusions.
- `results/*_F_steps.csv`: the exact fixed sequence and increment at every eligible archived check.
- `results/*_finite_masks.npz` and `*_finite_metadata.json`: the finite masks and exact source/parameter mapping used by F0/F1.
- `results/COMPLETE.json` and `results/SHA256_MANIFEST.json`: execution receipt, original input hashes, prediction agreement, runtime and output hashes.

Fresh reconstruction from the project root:

```bash
python r4_analysis/disagreement/run_saved_paths.py --recompute
```

The command writes only its own `results/` folder; original evidence and R3 remain immutable. The independent numerical agent is separately reconstructing the central D/F findings from raw archived evidence for the final R4 review record.

## Interpretation limits

The saved finite grid establishes observed disagreement and sampled returns. A bracket does not identify a unique first continuous crossing, and agreement at every sampled penalty does not establish agreement between samples or beyond the grid. B remains a sufficient tail bound. The five seeds reuse evaluation images, so audit path counts are not independent sample sizes. Probe counts are operation-count diagnostics; they do not establish measured speedups or a prospective safe stopping rule. The limiting calculation also requires training-derived matrix products. No additional training or paid compute was used.
