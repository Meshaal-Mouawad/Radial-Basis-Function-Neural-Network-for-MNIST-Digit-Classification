#!/usr/bin/env python3
"""Publication plots of archived-model diagnostics; no fitting."""
import csv
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
HERE=Path(__file__).resolve().parent
rows=list(csv.DictReader((HERE/'results/surface_per_model.csv').open()))
best=list(csv.DictReader((HERE/'results/validation_best_per_seed.csv').open()))
summary=list(csv.DictReader((HERE/'results/validation_best_summary.csv').open()))
out=HERE/'figures';out.mkdir(exist_ok=True)
plt.rcParams.update({'font.family':'DejaVu Sans','font.size':9,'axes.spines.top':False,'axes.spines.right':False,'axes.labelcolor':'#273844','text.color':'#273844','axes.edgecolor':'#74838D','pdf.fonttype':42,'ps.fonttype':42})
fig,ax=plt.subplots(2,3,figsize=(8.5,5.7),sharex=True,sharey=True)
for di,ds in enumerate(['mnist','fashion_mnist']):
 for ki,K in enumerate([50,100,200]):
  a=ax[di,ki];rr=[r for r in rows if r['dataset']==ds and int(r['K'])==K];non=[r for r in rr if r['competitive95']=='False'];comp=[r for r in rr if r['competitive95']=='True']
  a.scatter([float(r['certificate_coverage_pct']) for r in non],[float(r['evaluation_accuracy_pct']) for r in non],s=8,color='#A9B8C1',alpha=.45,linewidth=0,label='Other archived models',rasterized=False)
  a.scatter([float(r['certificate_coverage_pct']) for r in comp],[float(r['evaluation_accuracy_pct']) for r in comp],s=14,facecolors='none',edgecolors='#267F8C',linewidth=.6,label='Validation accuracy ≥95% of best')
  a.set_title(('MNIST' if ds=='mnist' else 'Fashion-MNIST')+f', K={K}',fontsize=10);a.set_xlim(-3,103);a.set_ylim(0,100);a.set_xticks([0,25,50,75,100]);a.grid(True,linewidth=.35,alpha=.25);a.set_axisbelow(True)
  if ki==0:a.set_ylabel('Evaluation accuracy (%)')
  if di==1:a.set_xlabel('Full-width certificate coverage (%)')
  a.text(.96,.05,f'{len(comp)} of 480 retained',transform=a.transAxes,ha='right',fontsize=8)
handles,labels=ax[0,0].get_legend_handles_labels();fig.legend(handles,labels,loc='lower center',ncol=2,frameon=False,bbox_to_anchor=(.5,-.015));fig.tight_layout(rect=(0,.03,1,1));fig.savefig(out/'competitive_accuracy_coverage.pdf',bbox_inches='tight');fig.savefig(out/'competitive_accuracy_coverage.png',dpi=180,bbox_inches='tight');plt.close(fig)
fig,ax=plt.subplots(1,2,figsize=(8.5,3.3))
for di,ds in enumerate(['mnist','fashion_mnist']):
 a=ax[di]
 for seed in [11,22,33,44,55]:
  rr=sorted([r for r in best if r['dataset']==ds and int(r['seed'])==seed],key=lambda r:int(r['K']));a.plot([int(r['K']) for r in rr],[float(r['evaluation_accuracy_pct']) for r in rr],color='#B1C1C9',lw=.7,marker='o',ms=3,alpha=.8)
 ss=sorted([r for r in summary if r['dataset']==ds],key=lambda r:int(r['K']));a.errorbar([int(r['K']) for r in ss],[float(r['evaluation_accuracy_pct_mean']) for r in ss],yerr=[float(r['evaluation_accuracy_pct_sd']) for r in ss],color='#267F8C',lw=1.7,marker='o',ms=5,capsize=3,label='Five-seed mean ± SD')
 a.set_title('MNIST' if ds=='mnist' else 'Fashion-MNIST');a.set_xticks([50,100,200]);a.set_xlabel('Prototype budget K');a.set_ylabel('Evaluation accuracy (%)');a.grid(True,linewidth=.35,alpha=.25);a.set_axisbelow(True)
ax[1].legend(frameon=False,fontsize=8,loc='lower right');fig.tight_layout();fig.savefig(out/'validation_selected_budget_accuracy.pdf',bbox_inches='tight');fig.savefig(out/'validation_selected_budget_accuracy.png',dpi=180,bbox_inches='tight');plt.close(fig)
print(str(out))
