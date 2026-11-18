"""Reuse R3 query records; no training or parameter selection."""
import argparse,csv,json,hashlib
from pathlib import Path
import numpy as np
p=argparse.ArgumentParser();p.add_argument('--results',type=Path,required=True);p.add_argument('--out',type=Path,required=True);a=p.parse_args();a.out.mkdir(parents=True,exist_ok=True)
rows=[];classes=[];hashes={}
for path in sorted(a.results.glob('*.npz')):
 hashes[path.name]=hashlib.sha256(path.read_bytes()).hexdigest()
 dataset,seed=path.stem.split('_seed');seed=int(seed.split('_')[0])
 with np.load(path) as z:
  y=z['truth']
  for t,width in enumerate([.5,1.]):
   pred=z[f't{t}_predictions'];cert=z[f't{t}_certificate_mask'];gated=z[f't{t}_agreement_gated_distance_margin_mask']
   for selector,mask in [('certificate',cert),('gated_distance',gated)]:
    recall=[];retention=[];conditional=[]
    for c in range(10):
     allc=y==c;n=int(allc.sum());selected=int((allc&mask).sum());correct=int((allc&mask&(pred==y)).sum())
     recall.append(correct/n);retention.append(selected/n)
     if selected:conditional.append(correct/selected)
     classes.append(dict(dataset=dataset,seed=seed,width=width,selector=selector,truth_class=c,total=n,selected=selected,correct=correct))
    pc=np.bincount(pred[mask],minlength=10)/mask.sum();positive=pc[pc>0]
    rows.append(dict(dataset=dataset,seed=seed,width=width,selector=selector,coverage=100*mask.mean(),accuracy=100*np.mean(pred[mask]==y[mask]),macro_accepted_recall=100*np.mean(recall),selected_class_macro_accuracy=100*np.mean(conditional),represented_true_classes=len(conditional),predicted_classes=int((pc>0).sum()),effective_predicted_classes=float(np.exp(-sum(positive*np.log(positive)))),minimum_class_retention=100*min(retention),jaccard_certificate_gated=float((cert&gated).sum()/(cert|gated).sum()),identical_sets=bool(np.array_equal(cert,gated))))
def write(name,rs):
 with (a.out/name).open('w',newline='') as f:
  w=csv.DictWriter(f,fieldnames=rs[0]);w.writeheader();w.writerows(rs)
write('selection_diagnostics_per_seed.csv',rows);write('selection_diagnostics_classes.csv',classes)
summary=[]
for dataset in ['mnist','fashion_mnist']:
 for width in [.5,1.]:
  for selector in ['certificate','gated_distance']:
   sub=[r for r in rows if r['dataset']==dataset and r['width']==width and r['selector']==selector]
   out=dict(dataset=dataset,width=width,selector=selector)
   for key in list(rows[0])[4:]:
    vals=[r[key] for r in sub];out[key+'_mean']=float(np.mean(vals));out[key+'_sd']=float(np.std(vals,ddof=1))
   summary.append(out)
write('selection_diagnostics_summary.csv',summary)
# Independent count identities validate the derived metrics.
for r in rows:
 cc=[c for c in classes if all(c[k]==r[k] for k in ['dataset','seed','width','selector'])]
 assert len(cc)==10
 assert abs(100*sum(c['correct'] for c in cc)/sum(c['selected'] for c in cc)-r['accuracy'])<1e-10
 assert abs(10*sum(c['correct']/c['total'] for c in cc)-r['macro_accepted_recall'])<1e-10
 if r['dataset']=='fashion_mnist':assert abs(r['macro_accepted_recall']-r['coverage']*r['accuracy']/100)<1e-10
assert all(r['identical_sets'] for r in rows if r['dataset']=='mnist' and r['width']==1)
(a.out/'verification.json').write_text(json.dumps(dict(status='PASS',settings=20,selector_rows=len(rows),class_rows=len(classes),fits=0,input_sha256=hashes),indent=2)+'\n')
print(json.dumps(summary,indent=2))
