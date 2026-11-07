#!/usr/bin/env python3
"""Descriptive analysis of completed frozen study; no model fitting or selection."""
import csv
import hashlib
import json
from pathlib import Path

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np

ROOT = Path(__file__).resolve().parent
R = ROOT / 'results'
F = ROOT / 'figures'
F.mkdir(exist_ok=True)


def read_csv(name):
    with (R/name).open() as f:
        return list(csv.DictReader(f))


def descript(values):
    a=np.asarray(values,dtype=float)
    return {'mean':float(a.mean()),'sample_sd':float(a.std(ddof=1)),
            'minimum':float(a.min()),'maximum':float(a.max()),'values':a.tolist()}


tests=read_csv('test_metrics.csv')
valid=read_csv('validation_grid.csv')
eq=read_csv('rls_equivalence.csv')
feature=read_csv('feature_diagnostics.csv')
seeds=[11,22,33,44,55]
conditions=['nearest_prototype','fixed_1_pinv','fixed_1_lambda_1','scale_1_pinv','scale_1_lambda_1','validation_selected']
summaries={c:descript([100*float(r['test_accuracy']) for r in tests if r['condition']==c]) for c in conditions}
paired=[]
for seed in seeds:
    z=np.load(R/f'seed_{seed}_predictions.npz')
    y=z['test_y']
    for comparison,a,b in [('bandwidth_at_pinv','fixed_1_pinv','scale_1_pinv'),
                           ('bandwidth_at_lambda1','fixed_1_lambda_1','scale_1_lambda_1'),
                           ('selected_vs_nearest','nearest_prototype','validation_selected')]:
        ca,cb=z[a]==y,z[b]==y
        paired.append({'seed':seed,'comparison':comparison,
                       'percentage_point_change':float((cb.sum()-ca.sum())/len(y)*100),
                       'wrong_to_right':int(np.sum(~ca&cb)),'right_to_wrong':int(np.sum(ca&~cb)),
                       'both_right':int(np.sum(ca&cb)),'both_wrong':int(np.sum(~ca&~cb))})
with (R/'paired_differences.csv').open('w',newline='') as f:
    w=csv.DictWriter(f,fieldnames=list(paired[0]));w.writeheader();w.writerows(paired)
summary={'study_status':'completed new study on 2026-11-06',
         'test_accuracy_percent':summaries,
         'paired_percentage_point_changes':{c:descript([r['percentage_point_change'] for r in paired if r['comparison']==c]) for c in dict.fromkeys(r['comparison'] for r in paired)},
         'rls':{'checks':len(eq),'max_relative_weight_error':max(float(r['relative_weight_error']) for r in eq),
                'max_absolute_test_score_error':max(float(r['max_absolute_test_score_error']) for r in eq),
                'total_prediction_disagreements':sum(int(r['test_prediction_disagreements']) for r in eq),
                'solver_seconds':descript([float(r['rls_solver_seconds']) for r in eq]),
                'batch_svd_seconds_each_seed_and_width':descript([float(r['factorization_seconds']) for r in feature])},
         'activation_median_by_width':{w:descript([float(r['train_activation_median']) for r in feature if r['width']==w]) for w in ['fixed_1','scale_025','scale_05','scale_1']},
         'fraction_activations_below_1e_12_by_width':{w:descript([float(r['train_activation_fraction_below_1e_12']) for r in feature if r['width']==w]) for w in ['fixed_1','scale_025','scale_05','scale_1']},
         'interpretation':{'sd':'Descriptive sample SD across seed-specific split/prototype draws; all seeds share the 10000 test images.',
                           'solver':'RLS and batch ridge solve the same fixed-feature penalized least-squares objective when lambda=1/alpha.',
                           'timing':'One execution per condition; precomputed features; not a repeated performance benchmark.',
                           'novelty':'Known mathematical relationship; the measurements are a controlled case study, not evidence of a new learning algorithm.',
                           'boundary':'Single dataset, 100 random centers, 20000 training examples, four-width and seven-penalty grids.'}}
(R/'summary.json').write_text(json.dumps(summary,indent=2)+'\n')

plt.rcParams.update({'font.family':'DejaVu Sans','font.size':9,'axes.spines.top':False,'axes.spines.right':False,
                     'axes.labelcolor':'#243847','text.color':'#243847','xtick.color':'#243847','ytick.color':'#243847',
                     'axes.edgecolor':'#9caab2','savefig.bbox':'tight'})
labels=['Nearest\nprototype','Fixed width\nSVD','Fixed width\nridge','Scaled width\nSVD','Scaled width\nridge','Validation\nselected']
colors=['#abb5bf','#82a9bd','#82a9bd','#76aaa7','#76aaa7','#8d89b4']
fig,ax=plt.subplots(figsize=(7.2,3.65))
for i,c in enumerate(conditions):
    vals=np.array(summaries[c]['values'])
    ax.scatter(np.full(5,i)+np.linspace(-.10,.10,5),vals,c=colors[i],s=23,zorder=3,edgecolors='white',linewidths=.5)
    ax.errorbar(i,vals.mean(),yerr=vals.std(ddof=1),fmt='_',markersize=20,color='#243847',capsize=4,linewidth=1.1,zorder=4)
ax.set_xticks(range(len(conditions)),labels)
ax.set_ylabel('Test accuracy (%)')
ax.set_ylim(63,92)
ax.set_yticks([65,70,75,80,85,90])
ax.grid(axis='y',color='#e7ebed',linewidth=.7)
ax.set_axisbelow(True)
fig.text(.12,.98,'Five matched split and prototype draws',ha='left',va='top',fontsize=10)
fig.tight_layout(rect=(0,0,1,.95))
for ext in ['pdf','svg','png']:
    fig.savefig(F/f'accuracy_comparison.{ext}',dpi=220)
plt.close(fig)

widths=['fixed_1','scale_025','scale_05','scale_1']
lambdas=[0.,100.,10.,2.,1.,.1,.01]
matrix=np.array([[np.mean([100*float(r['validation_accuracy']) for r in valid if r['width']==w and float(r['lambda'])==l]) for l in lambdas] for w in widths])
fig,ax=plt.subplots(figsize=(7.2,3.25))
im=ax.imshow(matrix,cmap='Blues',vmin=50,vmax=90,aspect='auto')
for i in range(4):
    for j in range(7):
        ax.text(j,i,f'{matrix[i,j]:.2f}',ha='center',va='center',fontsize=9,color='white' if matrix[i,j]>79 else '#243847')
ax.set_xticks(range(7),['0\n(SVD)','100','10','2','1','0.1','0.01'])
ax.set_yticks(range(4),['Fixed 1','0.25 × scale','0.5 × scale','1 × scale'])
ax.set_xlabel('Ridge penalty λ')
ax.set_ylabel('Gaussian width')
cb=fig.colorbar(im,ax=ax,pad=.03)
cb.set_label('Mean validation accuracy (%)')
fig.tight_layout()
for ext in ['pdf','svg','png']:
    fig.savefig(F/f'validation_grid.{ext}',dpi=220)
plt.close(fig)

lines=['# Completed controlled experiment evidence','',
       'New measurements executed on 6 November 2026. The supplied 10 April 2026 report and MATLAB code remain unchanged.','',
       '## Design and execution','',
       'Five seeds each use a stratified 20,000-image training subset and a disjoint 5,000-image validation subset drawn from the supplied 60,000-image training pool. All five use the same supplied 10,000-image test set. Each seed has 100 randomly chosen training prototypes. The frozen grid has four Gaussian widths and seven penalties, giving 140 validation fits. Validation selection is recorded before test scores are computed. Test conditions and the same-budget nearest-prototype comparator were declared before execution.','',
       '## Test accuracy','',
       '| Condition | Mean ± sample SD (%) | Minimum–maximum (%) |','|---|---:|---:|']
for c in conditions:
    s=summaries[c]
    lines.append(f"| {c} | {s['mean']:.3f} ± {s['sample_sd']:.3f} | {s['minimum']:.2f}–{s['maximum']:.2f} |")
lines+=['','Each run denominator is 10,000 images; SD summarizes split and prototype draws. The five test evaluations are correlated through their shared test images and overlapping training pools.','',
        '## Findings and interpretation','',
        f"At the same unregularized SVD readout, distance-scaled width increases accuracy by {summary['paired_percentage_point_changes']['bandwidth_at_pinv']['mean']:.3f} percentage points on average. This matched comparison holds prototypes, training subset, and readout fixed; the width changes.",
        f"Across 35 positive-penalty conditions, batch ridge and single-pass RLS have zero test-label disagreements. The largest relative Frobenius weight error is {summary['rls']['max_relative_weight_error']:.6g}; the largest absolute test-score difference is {summary['rls']['max_absolute_test_score_error']:.6g}. The calculation validates the known lambda=1/alpha relationship under these fixed features.",
        'All five validation selections use the full distance-scale width. Four select unregularized SVD; seed 33 selects lambda=0.01. The scale is the median off-diagonal pairwise prototype distance divided by sqrt(2), giving widths between 7.1427 and 7.3904.',
        'The closest-prototype baseline uses the same 100 random prototype labels. It controls prototype budget and distance representation, without training an output readout. It is not a full-training-set nearest-neighbor baseline.',
        '', '## Evidence boundaries','',
        'The study measures one image dataset, one prototype budget, random center selection, and one fixed validation grid. It establishes a controlled empirical contrast and numerical equivalence. It does not establish a new solver or a new RBF principle. The April report accuracy values are not treated as reproduced measurements.',
        'Timing is separated into distance construction, activation exponentiation, factorization, and RLS readout updating. The solver timings use precomputed features and a single execution, so they are descriptive runtime records. The script retains the full features for the equivalence audit; any streaming-state memory formula would be analytical, not a measured peak-memory claim.',
        '', '## Reproduction','',
        'Run `python run_study.py --data-dir <repository>/Code --output-dir <new-output-directory>` with NumPy, SciPy, scikit-learn, and threadpoolctl. The two original MAT hashes are checked before computation. The script uses float64 conversion before dividing by 255 and MATLAB-compatible image flattening. Run `python analyze_results.py` to reproduce descriptive summaries and figures from the recorded default results directory.',
        'The protocol JSON hash, run source hash, dependency versions, data hashes, and completed result hashes are recorded. Split, prototype, and test indices and all five diagnostic score matrices per seed are retained in the prediction archives. A synthetic ridge/RLS equivalence test precedes the dataset computation.',
        '', '## Editorial use','',
        'Use these new measurements for a manuscript about bandwidth control and matched batch/recursive readouts. Preserve the reported April results only as historical claims in an external audit. Novelty and journal readiness must be judged against prior RBF, regularized least-squares, and online-learning literature.']
(ROOT/'EVIDENCE_REPORT.md').write_text('\n'.join(lines)+'\n')
manifest={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(ROOT.rglob('*')) if p.is_file() and p.name!='MANIFEST_SHA256.json'}
(ROOT/'MANIFEST_SHA256.json').write_text(json.dumps(manifest,indent=2)+'\n')
print(json.dumps(summary,indent=2))
