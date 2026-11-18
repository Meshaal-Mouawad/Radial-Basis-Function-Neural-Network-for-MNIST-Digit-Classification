"""Generate the three integrated R3 tables from verified numerical CSVs."""
from pathlib import Path
import argparse, csv

def rows(p):
    with p.open() as f: return list(csv.DictReader(f))

def run(root, out):
    out.mkdir(parents=True, exist_ok=True)
    m1=rows(root/'r3_analysis/m1_m2/results/m1_summary.csv')
    p1=rows(root/'r3_analysis/m1_m2/results/m1_thresholds_per_seed.csv')
    m2=rows(root/'r3_analysis/m1_m2/results/m2_summary.csv')
    m3=rows(root/'r3_analysis/m3/results/summary.csv')
    labels={'mnist':'MNIST','fashion_mnist':'Fashion-MNIST'}
    pm=lambda a,b,n=2: f'${float(a):.{n}f}\\pm{float(b):.{n}f}$'
    table=[r'\begin{table}[!htbp]',r'\centering\small',r'\caption{Sufficient reversal thresholds and the validation-based competitive reference at $K=100$. Threshold columns are five-seed means of within-seed quantiles of $B/\|A_\sigma\|_2$ among strict limiting reversals. The competitive column gives the range across seeds of the largest qualifying penalty at the same width, divided by $\|A_\sigma\|_2$ and multiplied by $10^5$. The last column counts bounds strictly below that competitive maximum among eligible strict-reversal query--seed cases.}',r'\label{tab:r3-thresholds}',r'\begin{tabular}{@{}llrrrr@{}}',r'\toprule',r'Dataset & $\sigma/s_C$ & Median & 90th percentile & $10^5\lambda_{\rm comp}/\|A_\sigma\|_2$ & Below / eligible\\',r'\midrule']
    for ds in labels:
        for wi,w in [(4,'1/2'),(5,'1'),(6,'2')]:
            a=next(x for x in m1 if x['dataset']==ds and int(x['width_index'])==wi)
            vals=[float(x['competitive_max_normalized_same_width'])*1e5 for x in p1 if x['dataset']==ds and int(x['width_index'])==wi]
            table.append(f"{labels[ds] if wi==4 else ''} & ${w}$ & {float(a['normalized_threshold_q0.5_mean']):.3f} & {float(a['normalized_threshold_q0.9_mean']):.3f} & {min(vals):.2f}--{max(vals):.2f} & {a['bound_within_competitive_total']} / {int(a['eligible_strict_limit_total']):,} "+r'\\')
        table.append(r'\addlinespace')
    table += [r'\bottomrule',r'\end{tabular}',r'\end{table}']
    (out/'r3_threshold_table.tex').write_text('\n'.join(table)+'\n')
    table=[r'\begin{table}[!htbp]',r'\centering\small',r'\caption{Incremental limiting-vote exclusions at penalty floor zero. $F_0$ contains original finite probes; $F_1$ also includes archived frontier and local-tail readouts. $L_+$ combines limiting witnesses from the original and dense width grids. Entries are five-seed mean percentages of the full query set, with sample SD in percentage points. Each difference is calculated from exact query masks. All witnesses lie inside the requested region.}',r'\label{tab:r3-overlap}',r'\begin{tabular}{@{}llrrrr@{}}',r'\toprule',r'Dataset & $t/s_C$ & $F_0$ & $L_+\setminus F_0$ & $F_1$ & $L_+\setminus F_1$\\',r'\midrule']
    for ds in labels:
        for wi,w in [(2,'1/8'),(3,'1/4'),(4,'1/2'),(5,'1'),(6,'2')]:
            a=next(x for x in m2 if x['dataset']==ds and int(x['width_index'])==wi and float(x['penalty_floor'])==0)
            vals=[pm(a[k+'_mean_pct'],a[k+'_sd_pp'],3) for k in ['original_finite','limit_only_vs_original','all_archived_finite','limit_only_vs_all']]
            table.append(f"{labels[ds] if wi==2 else ''} & ${w}$ & "+' & '.join(vals)+r'\\')
        table.append(r'\addlinespace')
    table += [r'\bottomrule',r'\end{tabular}',r'\end{table}']
    (out/'r3_overlap_table.tex').write_text('\n'.join(table)+'\n')
    table=[r'\begin{table}[!htbp]',r'\centering\small',r'\caption{Endpoint accuracy at exactly matched per-seed coverage for the 1\% local band and penalty $10\|A_t\|_2$. Entries are five-seed means $\pm$ sample SD in percentage points. Random gives the exact expected subset accuracy. Gated selectors first require endpoint agreement with the nearest-prototype label. The coverage row applies to every selection method in its column.}',r'\label{tab:r3-selectors}',r'\begin{tabular}{@{}lrrrr@{}}',r'\toprule',r' & \multicolumn{2}{c}{MNIST} & \multicolumn{2}{c}{Fashion-MNIST}\\',r'\cmidrule(lr){2-3}\cmidrule(lr){4-5}',r'Selector / measure & $t=s_C/2$ & $t=s_C$ & $t=s_C/2$ & $t=s_C$\\',r'\midrule']
    for key,lab in [('coverage','Coverage (\\%)'),('certificate','Certificate'),('full_query','Random expectation'),('score_margin','Score margin'),('prototype_distance_margin','Distance margin'),('agreement_gated_score_margin','Gated score margin'),('agreement_gated_distance_margin','Gated distance margin')]:
        vals=[]
        for ds in labels:
            for w in [.5,1.]:
                a=next(x for x in m3 if x['dataset']==ds and float(x['t_over_sC'])==w and x['selector']==('certificate' if key=='coverage' else key))
                metric='coverage_pct' if key=='coverage' else 'accuracy_pct'
                vals.append(pm(a[metric+'_mean'],a[metric+'_sd']))
        table.append(lab+' & '+' & '.join(vals)+r'\\')
    table += [r'\bottomrule',r'\end{tabular}',r'\end{table}']
    (out/'r3_selector_table.tex').write_text('\n'.join(table)+'\n')

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--root',type=Path,default=Path(__file__).resolve().parents[2]);p.add_argument('--output',type=Path,required=True)
    a=p.parse_args();run(a.root,a.output)
