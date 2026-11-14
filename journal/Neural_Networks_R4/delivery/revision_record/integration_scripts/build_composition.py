"""Render verified class-composition metrics and integrate their LaTeX input."""
from pathlib import Path
import csv, json, hashlib, shutil
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'r4_analysis/composition'; OUT.mkdir(exist_ok=True)
SRC=ROOT/'working_R4/source'
rows=list(csv.DictReader((ROOT/'next_work/results/selection_diagnostics_classes.csv').open()))
summary=list(csv.DictReader((ROOT/'next_work/results/selection_diagnostics_summary.csv').open()))
per=list(csv.DictReader((ROOT/'next_work/results/selection_diagnostics_per_seed.csv').open()))
assert json.loads((ROOT/'r4_analysis/independent/composition_verification.json').read_text())['status']=='PASS'
plt.rcParams.update({'font.family':'DejaVu Sans','font.size':9,'axes.spines.top':False,'axes.spines.right':False,'axes.labelcolor':'#263b4b','text.color':'#263b4b','axes.edgecolor':'#a7b6c0','xtick.color':'#52616d','ytick.color':'#52616d','pdf.fonttype':42,'svg.fonttype':'none'})
conditions=[('mnist',.5,'MNIST · $t=s_C/2$'),('mnist',1.,'MNIST · $t=s_C$'),('fashion_mnist',.5,'Fashion-MNIST · $t=s_C/2$'),('fashion_mnist',1.,'Fashion-MNIST · $t=s_C$')]
colors=['#193b56','#3e91b7'];selectors=['certificate','gated_distance']

def values(dataset,width,selector,metric):
    a=np.full((5,10),np.nan)
    for r in rows:
        if r['dataset']!=dataset or float(r['width'])!=width or r['selector']!=selector:continue
        s=[11,22,33,44,55].index(int(r['seed']));c=int(r['truth_class'])
        total,selected,correct=map(int,[r['total'],r['selected'],r['correct']])
        if metric=='selected_accuracy':a[s,c]=100*correct/selected if selected else np.nan
        elif metric=='retention':a[s,c]=100*selected/total
        else:a[s,c]=100*correct/total
    return a

for metric,label,name in [('selected_accuracy','Selected accuracy (%)','Figure_07_Selected_Class_Accuracy'),('retention','Class retained (%)','Supplement_Class_Retention'),('recall','Accepted recall (%)','Supplement_Accepted_Class_Recall')]:
    fig,axes=plt.subplots(2,2,figsize=(7.1,4.6),sharex=True,sharey=True)
    for ax,(dataset,width,title) in zip(axes.flat,conditions):
        for j,selector in enumerate(selectors):
            a=values(dataset,width,selector,metric)
            means=np.nanmean(a,axis=0)
            xs=np.arange(10)+(j-.5)*.32
            ax.bar(xs,means,width=.30,color=colors[j],label=['Certificate','Agreement-gated distance'][j],zorder=2)
            for i in range(5):
                ax.scatter(xs+(i-2)*.025,a[i],s=9,facecolors='white',edgecolors=colors[j],linewidth=.5,zorder=3)
        ax.set_title(title,loc='left',fontsize=10,fontweight='bold',pad=8)
        ax.set_xticks(range(10));ax.set_ylim(0,105);ax.set_yticks([0,25,50,75,100]);ax.grid(axis='y',color='#dde4e8',linewidth=.5,zorder=0)
        ax.tick_params(axis='x',labelbottom=True)
        if ax in axes[1,:]:ax.set_xlabel('True class')
    for ax in axes[:,0]:ax.set_ylabel(label)
    handles,labels=axes.flat[0].get_legend_handles_labels()
    fig.legend(handles,labels,loc='lower center',bbox_to_anchor=(.5,-.005),ncol=2,frameon=False,fontsize=9)
    fig.subplots_adjust(left=.10,right=.985,top=.94,bottom=.16,wspace=.11,hspace=.34)
    for ext in ['pdf','svg','png']:
        fig.savefig(OUT/(name+'.'+ext),dpi=190,bbox_inches='tight',pad_inches=.05)
    plt.close(fig)
    if metric=='selected_accuracy':
        for ext in ['pdf','svg','png']:shutil.copy2(OUT/(name+'.'+ext),SRC/(name+'.'+ext))

fig,ax=plt.subplots(figsize=(7.1,2.7))
for j,(dataset,width,title) in enumerate(conditions):
    vals=[float(r['jaccard_certificate_gated']) for r in per if r['dataset']==dataset and float(r['width'])==width and r['selector']=='certificate']
    ax.scatter(np.full(5,j)+np.linspace(-.1,.1,5),vals,s=36,c=colors[0],edgecolors='white',linewidth=.5,zorder=3)
    ax.plot([j-.18,j+.18],[np.mean(vals)]*2,color=colors[1],linewidth=2.5,zorder=4)
ax.set_xticks(range(4),[x[2] for x in conditions],fontsize=9);ax.set_ylabel('Certificate / gated-distance Jaccard');ax.set_ylim(0,1.04);ax.set_yticks([0,.25,.5,.75,1]);ax.grid(axis='y',color='#dde4e8',linewidth=.5)
fig.tight_layout()
for ext in ['pdf','svg','png']:fig.savefig(OUT/('Supplement_Selector_Overlap.'+ext),dpi=190,bbox_inches='tight',pad_inches=.05)
plt.close(fig)

lookup={(r['dataset'],float(r['width']),r['selector']):r for r in summary}
def f(key,selector):
 return [f"${float(lookup[(d,w,selector)][key+'_mean']):.2f}\\pm{float(lookup[(d,w,selector)][key+'_sd']):.2f}$" for d,w,_ in conditions]
lines=[r'\begin{table}[!htbp]',r'\centering\small',r'\caption{Composition at the same coverage as Table~\ref{tab:r3-selectors}. Selected-class accuracy gives equal weight to each true class represented in the selected set; accepted recall uses all ten full evaluation classes. Entries are five-seed means $\pm$ sample SD. Jaccard compares the two selectors within each seed.}',r'\label{tab:r4-composition}',r'\begin{tabular}{@{}lrrrr@{}}',r'\toprule',r' & \multicolumn{2}{c}{MNIST} & \multicolumn{2}{c}{Fashion-MNIST}\\',r'\cmidrule(lr){2-3}\cmidrule(lr){4-5}',r'Measure / selector & $s_C/2$ & $s_C$ & $s_C/2$ & $s_C$\\',r'\midrule']
for heading,key in [('Selected-class accuracy (\\%)','selected_class_macro_accuracy'),('Macro accepted recall (\\%)','macro_accepted_recall'),('Effective predicted classes','effective_predicted_classes')]:
 lines+=[r'\multicolumn{5}{@{}l}{'+heading+r'}\\']
 for s,l in [('certificate','Certificate'),('gated_distance','Gated distance')]:lines.append(l+' & '+' & '.join(f(key,s))+r'\\')
lines += [r'\midrule','Jaccard & '+' & '.join(f('jaccard_certificate_gated','certificate'))+r'\\',r'\bottomrule',r'\end{tabular}',r'\end{table}']
(SRC/'r4_composition_table.tex').write_text('\n'.join(lines)+'\n')
manifest={str(p.relative_to(OUT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in OUT.iterdir() if p.is_file() and p.name!='SHA256_MANIFEST.json'}
(OUT/'SHA256_MANIFEST.json').write_text(json.dumps(manifest,indent=2)+'\n')
print(json.dumps({'status':'PASS','figure_files':len(manifest),'table':str(SRC/'r4_composition_table.tex')}))
