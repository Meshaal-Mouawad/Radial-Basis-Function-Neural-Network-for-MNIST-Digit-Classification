# Independent R4 numerical audit

**Status: PASS.** Stages C-G were independently reconstructed from the preserved R2 image payloads, original prototype/split identities, and archived fitted weights. The audit imports neither R4 analysis runner nor the production certificate implementation. No readout was refitted.

## Audit scope and results

| Stage | Independently checked | Result |
|---|---|---|
| C: composition | 140,270 endpoint labels; 40 selector records; 400 class records; eight five-seed summaries | Exact labels, selectors, class counts and metric values |
| D: sampled penalty paths | 20,198,880 predictions; 3,366,480 query-width paths; 480 path-summary rows; 70 bound-comparison rows | Margins, guards, states, sampled brackets and sign changes reconstructed |
| E: competitive operating regions | 14,400,000 validation labels; 2,880 model conditions; 2,880 independently implemented sharp masks | Validation selections, coverage and exclusion surfaces reproduced |
| Preservation within E | 630 original endpoint/floor certificate masks | Exact reproduction |
| F: finite-probe accumulation | 1,161 finite-probe masks; 21,630 cumulative-probe rows; 420 region/bank summaries | Fixed ordering, all marginal counts and original/expanded R3 unions reproduced |
| G: stability | 300 selected-model class rows; 30 paired budget comparisons; 60 cross-seed comparisons | Query identities, paired metrics, class counts and overlaps reproduced |
| Final tables | Six validation-best summaries; 18 competitive summaries; six paired-budget summaries | Means, sample SDs and counts verified |

## Confirmed findings

- The 90%, 95% and 99% validation thresholds retain 494, 328 and 116 archived models, respectively. All retained models have zero full-width certificate coverage, across all 30 dataset/seed/prototype-budget groups.
- Strict disagreement is followed by a return to strict agreement in 190,405 of 3,366,480 query-width paths. A path can display five strict sign changes across the six sampled penalties. No path contains a guard-state or rank-invalid sample in these archived calculations.
- A sampled first disagreement and a sufficient finite reversal bound are distinct quantities. The audit verifies their stored comparisons and checks that archived penalties above the sufficient bound have positive competing score margins.
- All composition metrics use their declared denominators. Selected-class macro accuracy averages correctness within represented selected true classes; macro accepted recall uses full per-class evaluation populations.
- At MNIST t=s_C, every endpoint prediction is class 1, and certification and agreement-gated distance selection choose identical subsets in every seed.
- The finite-probe efficiency results are deterministic replay counts. All original and expanded exclusion masks reproduce R3 exactly. No new solve or measured wall-clock speedup is claimed by the audit.

Repeated labels and query-width paths are reconstruction counts. The experimental evaluation populations remain 4,027 MNIST and 10,000 Fashion-MNIST images, reused across seed realizations.

## Executable verification

The package root must contain `evidence/`, `r3_analysis/`, `r4_analysis/`, and `next_work/` in their supplied layout. From that root:

```bash
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 PYTHONDONTWRITEBYTECODE=1 \
  python r4_analysis/independent/verify_composition.py
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 PYTHONDONTWRITEBYTECODE=1 \
  python r4_analysis/independent/verify_competitive.py
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 PYTHONDONTWRITEBYTECODE=1 \
  python r4_analysis/independent/verify_paths_efficiency.py
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 PYTHONDONTWRITEBYTECODE=1 \
  python r4_analysis/independent/verify_summary_tables.py
```

NumPy, SciPy and threadpoolctl are required. The scripts write JSON receipts beside themselves. `summary_tables_verification.json` retains the exact SHA-256 values of the audited output arrays and tables. Each core receipt includes its verifier source hash and measured elapsed time.

## Scope of this verdict

This is a numerical verification verdict. It establishes that the new empirical claims are reconstructable and correctly calculated. Manuscript production, visual inspection, source preservation and the assessment of the scientific contribution have separate review records.
