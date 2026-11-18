from pathlib import Path
import csv,json
ROOT=Path(__file__).resolve().parents[2]; S=ROOT/'working_R4/source'
for f in ['composition','competitive','paths_efficiency']:
 assert json.loads((ROOT/f'r4_analysis/independent/{f}_verification.json').read_text())['status']=='PASS'
def table(name,caption,label,header,rows,align):
 lines=[r'\begin{table}[!htbp]',r'\centering\small',r'\caption{'+caption+'}',r'\label{'+label+'}',r'\begin{tabular}{@{}'+align+r'@{}}',r'\toprule',header+r'\\',r'\midrule']
 lines += [' & '.join(row)+r'\\' for row in rows]
 lines += [r'\bottomrule',r'\end{tabular}',r'\end{table}']
 (S/name).write_text('\n'.join(lines)+'\n')
def read(p):return list(csv.DictReader((ROOT/p).open()))
def v(r,key,suffix1='_mean_pct',suffix2='_sd_pp'):return f"${float(r[key+suffix1]):.2f}\\pm{float(r[key+suffix2]):.2f}$"
dnames={'mnist':'MNIST','fashion_mnist':'Fashion-MNIST'}
rows=[]
for r in read('r4_analysis/disagreement/results/D_summary.csv'):
 rows.append([dnames[r['dataset']],r['K']]+[v(r,k) for k in ['strict_disagreement_any','left_censored_first_disagreement','first_detected_after_zero','sampled_return_to_agreement']])
table('r4_paths_table.tex',r'Strict disagreement along the six sampled penalties $0,1,10,100,1000,10000$. Percentages are five-seed means $\pm$ sample SD across all 16 widths. Each seed contributes 64,432 query--width paths on MNIST or 160,000 on Fashion-MNIST. Initial disagreement and first detection after zero partition the any-disagreement column. Return denotes a later strict agreement after a sampled disagreement.','tab:r4-paths',r'Dataset & $K$ & Any (\%) & At zero (\%) & First later (\%) & Return (\%)',rows,'llrrrr')
rows=[]
for r in read('r4_analysis/competitive/results/validation_best_summary.csv'):
 rows.append([dnames[r['dataset']],r['K']]+[v(r,k,'_mean','_sd') for k in ['evaluation_accuracy_pct','nearest_agreement_pct','combined_region_exclusion_pct']])
table('r4_competitive_table.tex',r'Validation-selected archived models across all 30 groups. Entries are five-seed means $\pm$ sample SD with the full evaluation set as denominator. All selected models use $\lambda=0$ and have zero sharp full-width coverage. Exclusion concerns the requested region $(0,\sigma]\times[\lambda,\infty)$ attached to the selected endpoint.','tab:r4-competitive',r'Dataset & $K$ & Accuracy (\%) & Nearest agreement (\%) & Region excluded (\%)',rows,'llrrr')
rows=[]
for d in ['mnist','fashion_mnist']:
 for r in read('r4_analysis/disagreement/results/F_aggregate.csv'):
  if r['dataset']==d and r['width_index']=='5' and r['penalty_floor']=='0':
   reached=int(r['probes_to_capture95pct_L0_available_seeds'])
   count=f"{float(r['probes_to_capture95pct_L0_mean']):.1f}" if reached else r'---'
   rows.append([dnames[d],r['probe_set'],f"{float(r['eligible_archived_probes_mean']):.1f}",f'{reached}/5',count,f"{float(r['L0_unique_mean_pct']):.3f}"])
table('r4_probe_table.tex',r'Fixed-order accumulation at $t=s_C$ and penalty floor zero. Checks are archived readout evaluations in the recorded round-robin order. The recovery target is 95\% of the original limiting-witness set $L_0$ within each seed. Means use five seeds; a dash means the target was not reached. The final column has the full query population as denominator.','tab:r4-probes',r'Dataset & Set & Eligible checks & Reaching target & Checks to target & $L_0$ unique (\%)',rows,'llrrrr')
methods=r'''
\subsection{Finite disagreement paths and ordered witness accumulation}
\label{sec:r4-path-design}
We reconstruct the normalized class scores of all 96 archived readouts in every dataset--seed--budget group: 16 widths and six penalties $0,1,10,100,1000,10000$. For each query and width, the signed margin is the largest competing-class score minus the nearest-prototype class score. A margin above $10^{-10}(1+|\text{competing score}|+|\text{reference score}|)$ defines strict disagreement; a margin below the negative guard defines strict agreement. Zero-penalty records also require the archived numerical full-rank condition. The first sampled disagreement is recorded at zero, after zero with its adjacent sampled bracket, or as undetected through 10,000. All later sign changes and returns to strict agreement are retained. Comparisons with $B(x,\sigma)$ use exactly the seven available widths in the $K=100$ groups, retaining missing bound references separately from absence of a strict limiting reversal.

For the same seven upper widths and three floors used in Section~\ref{sec:r3-design}, we accumulate the original finite probes $F_0$ and expanded probes $F_1$ in a fixed order. After filtering to the requested region, widths are sorted ascending; within a width, penalties are sorted ascending with a fixed archive-source tie-break. The checks then interleave across widths: first eligible penalty at each width, then second, and so on. Every step records new and cumulative finite exclusions, overlap with $L_0$ and $L_+$, and their augmented unions. We retain the first prefix recovering 95\% or all of $L_0$, and the first prefix recovering each final exclusion set. These analyses replay stored weights and perform zero new readout fits.

\subsection{Validation-competitive models and budget stability}
\label{sec:r4-competitive-design}
The validation analysis covers all 30 original groups: two datasets, five seeds, and $K\in\{50,100,200\}$. Each group's 96 archived readouts is scored on its 5,000 validation observations. We select the largest validation correct count, resolving ties by smaller bandwidth and then smaller penalty. Evaluation targets are scored after fixing the selection. Retained competitive sets use at least 95\% of the group's maximum validation accuracy, with fixed 90\% and 99\% sensitivity thresholds. At every archived pair $(\sigma,\lambda)$, we evaluate the sharp certificate for $(0,\sigma]\times[\lambda,\infty)$ and the union of strict limiting and finite witnesses in that region. This analysis uses all original probe widths up to $\sigma$ for limiting witnesses. The exclusion fraction counts queries whose requested family contains a strict disagreement.

Within each seed, budget comparisons pair the selected models on the same query identifiers. Across seeds, the ten pairs per dataset and budget give descriptive prediction-disagreement rates and Jaccard overlap of correctly classified queries. Per-class recall and predicted-class counts are retained for all 30 selected models. Independent implementations reconstruct the 2,880 model records from raw images and archived weights, verify 14.4 million validation prediction labels and 20,198,880 evaluation labels, and recompute the sharp masks directly from the equations. Separate reconstruction verifies all 3,366,480 query--width path records and 21,630 ordered cumulative exclusion records.
'''
# Idempotent append to the composition-only input.
p=S/'r4_methods.tex'; prior=p.read_text().split('\\subsection{Finite disagreement paths')[0].rstrip();p.write_text(prior+'\n'+methods)
results=r'''
\subsection{Observed disagreement and returns along the penalty path}
\label{sec:r4-path-results}
Nearest-prototype agreement is nonmonotone along the sampled regularization paths. Table~\ref{tab:r4-paths} reports the complete grid. A later sampled penalty restores strict agreement in 4.02--6.02\% of MNIST paths and 5.39--6.40\% of Fashion-MNIST paths, depending on prototype budget. Across all groups, 190,405 of 3,366,480 audited query--width paths return to strict agreement after an earlier disagreement. The largest observed number of sign changes is five across the six penalties. For example, Fashion-MNIST seed 22 with $K=100$, width $1.5s_C$, and query 50 alternates between strict agreement and disagreement at every sampled penalty; its competing-minus-reference margins are approximately $-0.017925$, $0.040578$, $-0.033922$, $0.009067$, $-0.017918$, and $0.011859$. Every margin in the exhaustive grid lies outside the numerical guard.

\input{r4_paths_table.tex}

The sufficient reversal bound and the first sampled disagreement describe different parts of these paths. At $t=s_C$, all 16,755 finite MNIST bounds and 33,135 finite Fashion-MNIST bounds exceed 10,000. Within those records, 9,714 and 19,154 respectively already disagree at a sampled smaller penalty. A further 878 MNIST and 8,808 Fashion-MNIST records show finite disagreement without a strict limiting reversal at that endpoint. At $t=s_C/2$, all 10,335 MNIST and 5,728 Fashion-MNIST sampled query--penalty pairs above their finite sufficient bounds have positive competing margins. Thus the tail guarantee, sampled onset, and sampled returns are separately recoverable from the same archived family.

\subsection{Coverage at validation-competitive operating points}
\label{sec:r4-competitive-results}
Every validation-competitive archived model has zero sharp full-width certificate coverage. The primary 95\% rule retains 328 models across all 30 groups; the 90\% and 99\% rules retain 494 and 116, respectively, with the same zero-coverage result. Table~\ref{tab:r4-competitive} reports the best-validation choice in each group. All 30 select zero penalty, with widths between $0.75s_C$ and $2s_C$. Evaluation accuracy rises from 82.92\% to 91.80\% across the three MNIST budgets and from 76.23\% to 82.13\% on Fashion-MNIST. The requested full-width regions are excluded for 77.30--98.23\% of Fashion-MNIST queries and 87.53--88.24\% of MNIST queries. These exclusions identify the fraction whose nearest-prototype label fails somewhere inside the family attached to the selected operating point.

\input{r4_competitive_table.tex}

Increasing prototype budget improves the evaluation accuracy of the validation-selected readout at each budget step in every seed of both datasets. The paired $K=50$ to $K=200$ gain is $8.88\pm0.41$ percentage points on MNIST and $5.90\pm0.80$ on Fashion-MNIST. Across the ten seed pairs, mean prediction disagreement falls from 14.29\% to 5.95\% on MNIST and from 12.21\% to 8.15\% on Fashion-MNIST. Mean Jaccard overlap of correctly classified queries rises from 0.874 to 0.947 and from 0.885 to 0.922, respectively. The supplement retains every paired value, all class counts, and accuracy--coverage plots for all 2,880 readouts.

\subsection{Accumulation of exclusions under a fixed finite-probe order}
\label{sec:r4-probe-results}
Expanded finite probes recover most original limiting-witness cases early in the recorded sequence. At $t=s_C$ and floor zero, $F_1$ reaches 95\% of $L_0$ after mean 15.6 MNIST and 20.2 Fashion-MNIST checks, in all five seeds (Table~\ref{tab:r4-probes}). The original finite set $F_0$ never reaches this target in these ten groups. All $L_0$ cases are recovered by $F_1$ on MNIST after mean 17.6 checks. On Fashion-MNIST, $L_0$ retains a unique set comprising 0.134\% of all queries after the full expanded sequence. The final $F_1$ finite exclusion set is recovered after mean 49.6 of 100.8 eligible checks on MNIST and 107.4 of 107.4 on Fashion-MNIST. The stored step records identify which additional widths and penalties supply each increment.

\input{r4_probe_table.tex}
'''
p=S/'r4_results.tex';prior=p.read_text().split('\\subsection{Observed disagreement')[0].rstrip();p.write_text(prior+'\n'+results)
print('R4 methods, results, and three exact-data tables integrated')
