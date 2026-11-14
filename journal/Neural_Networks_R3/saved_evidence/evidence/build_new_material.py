from pathlib import Path
import csv
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np

ROOT=Path(__file__).resolve().parent
OUT=ROOT/'manuscript'; OUT.mkdir(exist_ok=True)
DATA=ROOT/'new_analysis'/'limit_diagnostic'
def rows(path):
    with path.open(newline='') as f: return list(csv.DictReader(f))
part=rows(DATA/'original7_guarded'/'summary.csv')
tail=rows(DATA/'local_tail'/'summary.csv')
acc=rows(DATA/'local_tail_validation'/'all_query_summary.csv')
def p_row(d,i): return next(r for r in part if r['dataset']==d and int(r['width_index'])==i and float(r['lambda_floor'])==0)
def t_row(d,t,m): return next(r for r in tail if r['dataset']==d and float(r['t_over_sC'])==t and float(r['s_over_t'])==.99 and r['method']==m)
def a_row(d,t): return next(r for r in acc if r['dataset']==d and float(r['t_over_sC'])==t and float(r['lambda_over_At_operator'])==10)
def val(r,k): return float(r[k])
def ms(r,k,s): return f"{val(r,k):.2f} $\\pm$ {val(r,s):.2f}"
names={'mnist':'MNIST','fashion_mnist':'Fashion-MNIST'}
plt.rcParams.update({'font.family':'DejaVu Sans','font.size':9,'axes.labelcolor':'#334155','text.color':'#203B50','axes.edgecolor':'#CBD5E1','pdf.fonttype':42,'ps.fonttype':42,'svg.fonttype':'none'})
fig,axes=plt.subplots(1,2,figsize=(7.0,3.8),sharey=True)
colors=['#237267','#203B50','#DCE3EA']; labels=['Certified','Excluded','Unresolved']
for ax,d,panel in zip(axes,names,['A','B']):
    rs=[p_row(d,i) for i in range(1,7)]
    left=np.zeros(6)
    for key,color,label in zip(['certified_mean_pct','combined_excluded_mean_pct','unresolved_mean_pct'],colors,labels):
        vv=np.array([val(r,key) for r in rs])
        ax.barh(np.arange(6),vv,left=left,height=.65,color=color,edgecolor='white',linewidth=.7,label=label)
        for j,v in enumerate(vv):
            if v>=10: ax.text(left[j]+v/2,j,f'{v:.1f}',ha='center',va='center',color='#203B50' if label=='Unresolved' else 'white',fontsize=9.2)
        left+=vv
    ax.set_title(f'{panel}  {names[d]}',loc='left',fontweight='normal',fontsize=11,pad=12)
    ax.set_xlim(0,100);ax.set_xticks([0,25,50,75,100]);ax.set_xlabel('Queries (%)')
    ax.set_yticks(range(6),['1/16','1/8','1/4','1/2','1','2'])
    ax.tick_params(axis='both',length=0,pad=5)
    for side in ['top','right','left']: ax.spines[side].set_visible(False)
    ax.spines['bottom'].set_color('#CBD5E1')
axes[0].set_ylim(5.6,-.6)
axes[0].set_ylabel(r'Upper bandwidth $t/s_C$')
handles,labs=axes[0].get_legend_handles_labels()
fig.legend(handles,labs,loc='lower center',ncol=3,frameon=False,bbox_to_anchor=(.52,.005),fontsize=9)
fig.subplots_adjust(left=.105,right=.96,top=.88,bottom=.22,wspace=.15)
for ext in ['pdf','svg','png']: fig.savefig(OUT/f'Figure_06_Agreement_Region_Diagnosis.{ext}',dpi=300,facecolor='white')
plt.close(fig)

methods=r'''\subsection{Post hoc region diagnosis and local-tail evaluation}
\label{sec:new-design}
The additional analysis asks two questions: which uncertified parameter regions can be ruled out, and which local bandwidth bands admit a positive tail certificate? It reuses all ten $K=100$ dataset--seed groups, with the original training rows, prototype identities, evaluation queries, and labels. The analysis protocol was recorded before the new calculations, after inspecting the original frontier results. The original predictions and certificates remain the comparison baseline.

For each query and requested rectangle, we assign one of three outcomes: certified by Theorem~\ref{thm:agreement}; excluded by a strict opposing-label witness; or unresolved by either test. The limit witness evaluates Proposition~\ref{prop:ridge-limit} at all examined widths up to the upper endpoint. The finite witness reconstructs class scores from archived readout weights at widths within the rectangle and penalties at least its floor. A finite score tie supplies no witness. Zero-penalty witnesses additionally require full numerical column rank in the archived fit. Both numerical witnesses require the competing-minus-reference score to exceed $10^{-10}(1+|\text{competing score}|+|\text{reference score}|)$. We first use the seven original endpoints, then the existing 67-width grid to resolve the immediate neighborhood of the sufficient frontier. Every outcome uses the full query set as its denominator; we verify that certified and excluded masks are disjoint.

For the local-tail theorem, we evaluate $t/s_C\in\{1/2,1\}$ and $s/t\in\{0.99,0.95\}$. We normalize penalty thresholds by $\norm{A_t}_2$, consistent with the summed squared-error objective in Eq.~\eqref{eq:model}. The signed interval correction is compared with the direct positive-sum bound
\[
 \rho^{+}_{ab}(s,t)=\norm{A_t(Z_t[:,a]+Z_t[:,b])}_2,
\]
which follows from entrywise nonnegativity and supplies a comparator for the same local region and margin. The supplement retains query-specific thresholds and coverage at penalty multiples $1,10,100,10^3,10^4,10^6$. Queries failing any interval-margin condition receive an infinite threshold and remain in the denominator.

A separately recorded validation evaluates 120 new ridge readouts: ten dataset--seed groups, two upper widths, three fitted widths $0.95t,0.99t,t$, and penalties $10\norm{A_t}_2$ and $100\norm{A_t}_2$. We measure classification accuracy against dataset labels, agreement with the nearest-prototype label, and certified-subset accuracy. These fits validate finite predictions within the analytically certified bands. Reported means and sample standard deviations use the five seed realizations for each dataset. The supplement provides protocols, indexed inputs, all masks, fitted weights, predictions, executable scripts, and checksums.
'''
# Baseline model label is detected to avoid an invented cross-reference.
base=(ROOT/'baseline/source/main.tex').read_text()
if r'\label{eq:model}' not in base:
    methods=methods.replace(r' in Eq.~\eqref{eq:model}','')
(OUT/'new_methods.tex').write_text(methods)

result=r'''\subsection{Certified, excluded, and unresolved parameter regions}
\label{sec:region-diagnosis}
The three-way diagnostic separates sufficient coverage from demonstrated failure of the requested classifier family. Figure~\ref{fig:region-diagnosis} and Table~\ref{tab:region-diagnosis} report the original scaled endpoints at $K=100$ and penalty floor zero. At $t=s_C/8$, the sufficient certificate covers no queries, yet the combined witnesses exclude only 1.61\% of MNIST and 2.14\% of Fashion-MNIST queries. At $t=s_C$, the excluded proportions rise to 88.10\% and 84.48\%. The endpoint large-penalty witness alone accounts for 83.21\% and 66.27\%, respectively; narrower-width limit witnesses and archived finite predictions account for the remaining combined exclusions. Every certified/excluded intersection is empty.

\begin{figure}[!htbp]
\centering
\includegraphics[width=\textwidth]{Figure_06_Agreement_Region_Diagnosis.pdf}
\caption{Three outcomes for the original regions $(0,t]\times[0,\infty)$ at $K=100$. Certified denotes the original sufficient condition; excluded denotes the union of guarded strict large-penalty and archived finite-score witnesses; unresolved denotes the remaining queries. Bars show five-seed mean percentages, with labels for segments of at least 10\%; Table~\ref{tab:region-diagnosis} gives exact rounded values and seed variation. The change from unresolved to excluded at broader endpoints distinguishes missing guarantees from identified failures of whole-region agreement.}
\label{fig:region-diagnosis}
\end{figure}

\begin{table}[!htbp]
\centering\small
\caption{Outcome partition at the original scaled widths, $K=100$ and $\lambda_0=0$. Entries are five-seed means $\pm$ sample standard deviations in percentage points; denominators are 4,027 MNIST or 10,000 Fashion-MNIST queries per seed.}
\label{tab:region-diagnosis}
\begin{tabular}{llrrr}
\toprule
Dataset & $t/s_C$ & Certified (\%) & Excluded (\%) & Unresolved (\%)\\
\midrule
'''
ratios=['$1/16$','$1/8$','$1/4$','$1/2$','$1$','$2$']
for d in names:
    for i,ratio in enumerate(ratios,1):
        r=p_row(d,i)
        result += f"{names[d] if i==1 else ''} & {ratio} & {ms(r,'certified_mean_pct','certified_sd_pp')} & {ms(r,'combined_excluded_mean_pct','combined_excluded_sd_pp')} & {ms(r,'unresolved_mean_pct','unresolved_sd_pp')} \\\\\n"
    if d=='mnist':result+=r'\midrule'+'\n'
result+=r'''\bottomrule
\end{tabular}
\end{table}

The dense grid resolves the loss of sufficient coverage more precisely. For each seed, we inspect the first grid width after the largest width retaining any sharp certification. At floor zero, the mean upper widths are $0.09622s_C$ for MNIST and $0.08638s_C$ for Fashion-MNIST. The excluded proportions are only $0.38\pm0.15$\% and $0.44\pm0.32$\%, leaving 99.62\% and 99.56\% unresolved. These measurements place the sufficient frontier and the demonstrated broad-width obstruction in distinct regimes. The tests identify extensive failures farther into the bandwidth range and leave the immediate sufficient frontier open to tighter analysis.

\subsection{Local bandwidth bands with finite penalty thresholds}
\label{sec:tail-results}
Theorem~\ref{thm:local-tail} certifies positive local bandwidth bands at both broader endpoints. Table~\ref{tab:local-tail} reports $[0.99t,t]\times[10\norm{A_t}_2,\infty)$. At $t=s_C/2$, the signed interval condition covers 16.88\% of MNIST and 40.09\% of Fashion-MNIST queries. At $t=s_C$, it covers 16.79\% and 14.94\%. Retaining signs in the correction term materially changes coverage: at $t=s_C$, the positive-sum comparator covers 2.34\% of MNIST and no Fashion-MNIST queries at the same penalty floor. Among queries with positive interval margins, the mean within-seed median signed thresholds are $1.18\norm{A_t}_2$ and $1.38\norm{A_t}_2$ at $t=s_C/2$, and $1.14\norm{A_t}_2$ and $2.35\norm{A_t}_2$ at $t=s_C$.

\begin{table}[!htbp]
\centering\small
\caption{Local-band certification and fitted accuracy for $s=0.99t$ and penalty floor $\Lambda=10\norm{A_t}_2$, at $K=100$. Coverage refers to the full continuous band and tail; accuracy evaluates the fitted endpoint $(t,\Lambda)$ against dataset labels. Entries are five-seed means $\pm$ sample standard deviations in percentage points.}
\label{tab:local-tail}
\begin{tabular}{llrrr}
\toprule
 & & \multicolumn{2}{c}{Certified coverage (\%)} & Readout\\
Dataset & $t/s_C$ & Positive-sum & Signed interval & accuracy (\%)\\
\midrule
'''
for d in names:
    for t in [.5,1.]:
        rp=t_row(d,t,'positive_sum');rs=t_row(d,t,'signed_interval');ra=a_row(d,t)
        result+=f"{names[d] if t==.5 else ''} & {'$1/2$' if t==.5 else '$1$'} & {ms(rp,'certified_pct_at_10_times_operator_mean','certified_pct_at_10_times_operator_sd_pp')} & {ms(rs,'certified_pct_at_10_times_operator_mean','certified_pct_at_10_times_operator_sd_pp')} & {ms(ra,'readout_accuracy_pct_mean','readout_accuracy_pct_sd_pp')} \\\\\n"
    if d=='mnist':result+=r'\midrule'+'\n'
result+=r'''\bottomrule
\end{tabular}
\end{table}

Increasing the relative bandwidth span to $[0.95t,t]$ retains signed coverage of 16.77\% and 22.15\% at $t=s_C/2$ for MNIST and Fashion-MNIST, respectively. At $t=s_C$, coverage is 16.78\% for MNIST and zero for Fashion-MNIST. The interval-margin condition itself fails for every Fashion-MNIST query in that last setting. This sensitivity shows how the local width interval enters the guarantee.

Across the 120 newly fitted readouts, all 254,120 certified query--parameter checks agree with the nearest-prototype label. The corresponding all-query endpoint accuracies at $10\norm{A_t}_2$ are 15.60\% and 45.06\% at $t=s_C/2$, and 11.77\% and 29.86\% at $t=s_C$, for MNIST and Fashion-MNIST respectively. For the 1\% bands, certified-subset accuracies are 69.09\% and 75.27\% at $s_C/2$, and 68.93\% and 64.65\% at $s_C$. The new regions establish computable label agreement at broader widths and identify its penalty-dependent accuracy tradeoff. Together with the exclusion analysis, they characterize which classifier families can share the prototype summary.
'''
(OUT/'new_results.tex').write_text(result)
print('Created new methods/results inputs and Figure 6 from authoritative guarded CSV records.')
