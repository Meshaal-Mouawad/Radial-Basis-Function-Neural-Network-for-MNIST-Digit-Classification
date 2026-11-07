#!/usr/bin/env python3
"""Summarize completed supplementary records; does not alter models or selection."""
import csv,hashlib,json
from pathlib import Path
import numpy as np
HERE=Path(__file__).resolve().parent;OUT=HERE/'results'
def read(p):return list(csv.DictReader(p.open()))
def number(r,k):return float(r[k])
def csvwrite(p,rows):
    with p.open('w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
    complete=json.loads((OUT/'COMPLETE.json').read_text());eps=read(OUT/'endpoint_metrics.csv');cov=read(OUT/'grid_coverage.csv');front=read(OUT/'query_frontier_summary.csv')
    aggregated=[]
    for dataset in ['mnist','fashion_mnist']:
        for K in [50,100,200,'all']:
            for lo in [0,1,100]:
                for target in ['any','50pct','90pct']:
                    rows=[r for r in eps if r['dataset']==dataset and (K=='all' or int(r['K'])==K) and int(r['lambda_floor'])==lo and r['target']==target]
                    valid=[r for r in rows if r['available']=='True'];a=dict(dataset=dataset,K=K,lambda_floor=lo,target=target,groups=len(rows),available_groups=len(valid))
                    for key in ['sigma_over_sC','coverage','accuracy','nearest_accuracy','nearest_agreement','certified_accuracy','best_frozen_sampled_accuracy','accuracy_loss_vs_best_frozen_pp']:
                        values=[number(r,key) for r in valid];a[key+'_mean']=float(np.mean(values)) if values else '';a[key+'_min']=min(values) if values else '';a[key+'_max']=max(values) if values else ''
                    aggregated.append(a)
    csvwrite(OUT/'endpoint_summary_by_dataset_K_floor.csv',aggregated)
    lines=['# Supplementary post hoc bandwidth frontiers (M1)','',
      'The analysis brackets each query’s largest accepted guarded-certificate width and measures the fitted readout at widths selected from coverage alone. All 30 frozen dataset/seed/prototype groups and all three ridge floors are retained.','',
      '## Protocol and audit','',
      '- The final protocol and runner were hashed before execution in `FREEZE.json`. The 67-point geometric grid spans $s_C/32$ through $s_C/4$, with 22 intervals per doubling. Adjacent widths differ by $2^{1/22}=1.03200828$; each uncensored transition has a multiplicative bracket no wider than 3.21%.',
      '- The original `certificate.py` was imported unchanged, with its strict gap/tie guards. Every query/floor/method has a stored last passing index, next failing index, masks and left/right censor flags. Analytical monotonicity permits these brackets; every observed mask nesting relation was checked.',
      '- The largest sharp-certified width with any coverage, with at least 50% coverage, and with at least 90% coverage was selected independently for each group/floor. Choices used no evaluation targets. Each selected width was fitted using the archived thin-SVD ridge reference. All prediction archives were hashed before the separate evaluation-label files were scored.',
      '- The shared original widths $s_C/16$, $s_C/8$ and $s_C/4$ reproduce the frozen masks exactly. Method subset relations and numerical nesting pass. Every certified endpoint prediction agrees with the nearest-prototype label.',
      '- The first attempt stopped in the first group because a 65-point grid did not contain the two interior shared widths. Its source, protocol, freeze, environment and failure log are preserved in `attempt_01_aborted`. The corrected 67-point protocol was refrozen before any completed group archive or scoring.',
      f'- Completed local runtime: {complete["runtime_seconds"]:.1f} seconds. All {complete["coverage_rows"]:,} group/width/floor/method coverage rows and {complete["endpoint_rows"]} selected endpoint rows are archived.','',
      '## Measured operating frontiers','',
      'Entries below summarize the 15 groups per dataset (five seeds and three prototype budgets). Width and coverage ranges concern the largest grid width retaining at least one sharp-certified query. Accuracy, agreement and loss are arithmetic means across the 15 paired group outcomes.','',
      '| Dataset | Floor | Frontier $t/s_C$ range | Coverage at frontier range | Readout accuracy | Nearest agreement | Loss vs best frozen sampled accuracy |',
      '|---|---:|---:|---:|---:|---:|---:|']
    for a in aggregated:
        if a['K']!='all' or a['target']!='any':continue
        lines.append(f'| {a["dataset"]} | {a["lambda_floor"]} | {a["sigma_over_sC_min"]:.5f}–{a["sigma_over_sC_max"]:.5f} | {100*a["coverage_min"]:.2f}–{100*a["coverage_max"]:.2f}% | {100*a["accuracy_mean"]:.2f}% | {100*a["nearest_agreement_mean"]:.2f}% | {a["accuracy_loss_vs_best_frozen_pp_mean"]:.2f} pp |')
    largest_ratio=max(float(r['sigma_over_sC']) for r in eps if r['available']=='True' and r['target']=='any')
    overlap=np.exp(-1/largest_ratio**2)
    lines+=['',f'The largest accepted grid ratio across all groups and floors is {largest_ratio:.5f}; its Gaussian overlap at the median prototype distance is exp(−1/{largest_ratio:.5f}²) = {overlap:.2e}. The denser grid therefore locates the certification boundary within a regime where fitted labels remain almost identical to nearest-prototype labels. At these measured endpoints, broader sampled widths improve true-class accuracy by the paired losses reported above.']
    lines+=['','The $K=100$ groups used for the main figure have the following paired means and frontier ranges:','','| Dataset | Floor | Frontier $t/s_C$ mean (range) | Readout accuracy | Best frozen sampled accuracy | Paired accuracy loss |','|---|---:|---:|---:|---:|---:|']
    for a in aggregated:
        if a['K']!=100 or a['target']!='any':continue
        lines.append(f'| {a["dataset"]} | {a["lambda_floor"]} | {a["sigma_over_sC_mean"]:.5f} ({a["sigma_over_sC_min"]:.5f}–{a["sigma_over_sC_max"]:.5f}) | {100*a["accuracy_mean"]:.2f}% | {100*a["best_frozen_sampled_accuracy_mean"]:.2f}% | {a["accuracy_loss_vs_best_frozen_pp_mean"]:.2f} pp |')
    lines+=['','The comparison reference is the largest observed accuracy among the 16 frozen probe widths at the same ridge penalty, evaluated on the same queries. It is a descriptive post hoc sampled reference. No evaluation labels enter supplementary frontier or endpoint-width selection.','',
      '## Coverage targets','',
      '| Dataset | Floor | Target | Available groups / 15 | Mean selected $t/s_C$ | Mean actual coverage | Mean readout accuracy | Mean loss vs frozen reference |',
      '|---|---:|---|---:|---:|---:|---:|---:|']
    for a in aggregated:
        if a['K']!='all' or a['target']=='any':continue
        if a['available_groups']:
            lines.append(f'| {a["dataset"]} | {a["lambda_floor"]} | {a["target"]} | {a["available_groups"]}/15 | {a["sigma_over_sC_mean"]:.5f} | {100*a["coverage_mean"]:.2f}% | {100*a["accuracy_mean"]:.2f}% | {a["accuracy_loss_vs_best_frozen_pp_mean"]:.2f} pp |')
        else:lines.append(f'| {a["dataset"]} | {a["lambda_floor"]} | {a["target"]} | 0/15 | — | — | — | — |')
    lines+=['','## Censoring and zeros','',
      '| Dataset | Floor | Method | Left-censored query/group records | Right-censored query/group records |',
      '|---|---:|---|---:|---:|']
    for dataset in ['mnist','fashion_mnist']:
        for lo in [0,1,100]:
            for method in ['sharp','basic','cancellation_frobenius']:
                rows=[r for r in front if r['dataset']==dataset and int(r['lambda_floor'])==lo and r['method']==method]
                lines.append(f'| {dataset} | {lo} | {method} | {sum(int(r["left_censored"]) for r in rows):,} | {sum(int(r["right_censored"]) for r in rows):,} |')
    lines+=['','Counts are repeated query/group records; seeds and prototype budgets share evaluation images. Left censor means no grid width was accepted, so no positive frontier is assigned. Right censor means the frontier extends beyond the largest grid width. Complete zero coverage remains in `grid_coverage.csv`.','',
      '## Evidence files','',
      '- `results/grid_coverage.csv`: every dense-grid coverage result.',
      '- `results/endpoint_metrics.csv`: all selected endpoint metrics, missing targets and paired frozen-reference losses.',
      '- `results/endpoint_summary_by_dataset_K_floor.csv`: dataset/budget/floor/target summaries.',
      '- `results/query_frontier_summary.csv`: group frontier summaries and censor counts.',
      '- `results/<group>/frontiers_before_labels.npz`: per-query masks/brackets, indices, constants, endpoint predictions and weights.',
      '- `results/<group>/PREDICTIONS_FROZEN.json` and `results/ALL_PREDICTIONS_FROZEN.json`: chronology and hashes.',
      '- `results/training_diagnostics.csv`, `results/environment.json`, `results/progress.csv`, `results/MANIFEST_SHA256.json`: diagnostics and provenance.','',
      '## Limits','',
      'These are post hoc guarded-certificate grid brackets. A last accepted grid point is not an exact real-arithmetic maximal width; a left-censored query has no measured positive frontier. The supplementary endpoint checks use the selected rectangle endpoint; the frozen certificate supplies the continuum guarantee. Seed summaries are descriptive paired results from shared evaluation images and overlapping training pools. The 16-width accuracy reference is an observed sampled maximum.']
    difference=[]
    lookup={(r['dataset'],r['seed'],r['K'],r['lambda_floor'],r['grid_index'],r['method']):int(r['certified']) for r in cov}
    for dataset in ['mnist','fashion_mnist']:
        for lo in [0,1,100]:
            rows=[r for r in cov if r['dataset']==dataset and int(r['lambda_floor'])==lo and r['method']=='sharp']
            gaps=[int(r['certified'])-lookup[(dataset,r['seed'],r['K'],str(lo),r['grid_index'],'basic')] for r in rows]
            difference.append(dict(dataset=dataset,lambda_floor=lo,group_grid_conditions=len(rows),conditions_sharp_exceeds_basic=sum(g>0 for g in gaps),sum_query_condition_differences=sum(gaps),maximum_query_difference=max(gaps)))
    csvwrite(OUT/'sharp_basic_differences.csv',difference)
    insert_at=lines.index('## Limits')
    lines[insert_at:insert_at]=['## Sharp versus basic on the dense grid','','| Dataset | Floor | Conditions with more sharp coverage | Maximum added queries in one condition |','|---|---:|---:|---:|']+[f'| {r["dataset"]} | {r["lambda_floor"]} | {r["conditions_sharp_exceeds_basic"]}/{r["group_grid_conditions"]} | {r["maximum_query_difference"]} |' for r in difference]+['','This dense-grid comparison has its own declared scope. Original shared-width masks reproduce the frozen study exactly.','']
    (HERE/'REPORT.md').write_text('\n'.join(lines)+'\n')
    allbestbroader=all(number(r,'best_frozen_sampled_sigma')>number(r,'sigma') for r in eps if r['available']=='True')
    (HERE/'SUMMARY.json').write_text(json.dumps(dict(complete=complete,all_descriptive_best_frozen_widths_broader_than_selected_endpoints=allbestbroader,endpoint_targets_missing=sum(r['available']!='True' for r in eps)),indent=2)+'\n')
    print('\n'.join(lines[16:25]));print('all descriptive best frozen widths broader:',allbestbroader)
if __name__=='__main__':main()
