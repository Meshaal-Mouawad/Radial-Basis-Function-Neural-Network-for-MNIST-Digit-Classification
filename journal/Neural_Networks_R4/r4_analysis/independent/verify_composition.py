#!/usr/bin/env python3
"""Independent reconstruction of Stage C composition from raw R2 inputs."""
from pathlib import Path
import csv, gzip, hashlib, json, time
import numpy as np
from scipy.io import loadmat
from scipy.spatial.distance import cdist
from threadpoolctl import threadpool_limits

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
BASE=ROOT/'evidence/baseline/evidence/baseline'
EXP=BASE/'work/v2/experiment/results'
DIAG=ROOT/'evidence/new_analysis/limit_diagnostic'
RESULT=ROOT/'next_work/results'

def readcsv(p):
    with p.open() as f:return list(csv.DictReader(f))
def vectorize(x):return np.stack([v.ravel(order='F') for v in x]).astype(float)/255.
def images(p):
    b=gzip.decompress(p.read_bytes());s=np.frombuffer(b[:16],dtype='>u4');assert s[0]==2051
    return np.frombuffer(b[16:],np.uint8).reshape(tuple(s[1:]))
def yidx(p):return np.frombuffer(gzip.decompress(p.read_bytes())[8:],np.uint8).astype(int)
def top(scores,m,qids,eligible):
    ix=np.flatnonzero(eligible);rank=sorted(ix.tolist(),key=lambda k:(-scores[k],int(qids[k]),k))
    mask=np.zeros(len(scores),bool);mask[rank[:m]]=True
    return mask

def main():
    started=time.perf_counter();rows=readcsv(RESULT/'selection_diagnostics_per_seed.csv');classes=readcsv(RESULT/'selection_diagnostics_classes.csv');summaries=readcsv(RESULT/'selection_diagnostics_summary.csv')
    assert len(rows)==40 and len(classes)==400 and len(summaries)==8
    checked=0;classchecked=0;prediction_labels=0;generated=[];hashes={}
    def load(path):
        hashes[str(path.relative_to(ROOT))]=hashlib.sha256(path.read_bytes()).hexdigest()
        return np.load(path)
    for dataset in ['mnist','fashion_mnist']:
        if dataset=='mnist':
            p=BASE/'repository/Code/MNIST_train.mat';m=loadmat(p);x=m['imagestrain'].transpose(2,0,1);y=m['labelstrain'].ravel().astype(int);qi=np.load(BASE/'work/v2/design/reserved_training_ids.npy');qx=x[qi];truth=y[qi]
        else:
            p=BASE/'work/v2/data/fashion_mnist';x=images(p/'train-images-idx3-ubyte.gz');qx=images(p/'t10k-images-idx3-ubyte.gz');truth=yidx(p/'t10k-labels-idx1-ubyte.gz')
        Q=vectorize(qx)
        for seed in [11,22,33,44,55]:
            name=f'{dataset}_seed{seed}_K100';old=load(EXP/name/'predictions_before_labels.npz');tail=load(DIAG/'local_tail'/f'{name}.npz');fit=load(DIAG/'local_tail_validation'/f'{name}.npz')
            D=cdist(Q,vectorize(x[old['center_ids']]),'sqeuclidean');nearest=old['center_labels'][D.argmin(1)];assert np.array_equal(nearest,old['nearest_prototype']);scale=16*old['width_upper_bounds'][1];qid=old['query_ids'];n=len(truth)
            other=D.copy();other[old['center_labels'][None,:]==nearest[:,None]]=np.inf;distance=other.min(1)-D.min(1)
            for ri,ratio in enumerate([.5,1.]):
                t=ratio*scale;op=np.linalg.norm(tail[f'case{2*ri}_A_t'],ord=2);W=fit[f't{ri}_weights'][0,2];pred=(np.exp(-D/(2*t*t))@W).argmax(1);assert np.array_equal(pred,fit[f't{ri}_predictions'][0,2]);prediction_labels+=n
                cert=tail[f'case{2*ri}_threshold']<=10*op;assert np.all(pred[cert]==nearest[cert]);gated=top(distance,int(cert.sum()),qid,pred==nearest);assert cert.sum()==gated.sum()
                union=np.count_nonzero(cert|gated);jacc=np.count_nonzero(cert&gated)/union
                for selector,mask in [('certificate',cert),('gated_distance',gated)]:
                    rr=[r for r in rows if r['dataset']==dataset and int(r['seed'])==seed and float(r['width'])==ratio and r['selector']==selector];assert len(rr)==1;r=rr[0]
                    totals=np.bincount(truth,minlength=10);selected=np.bincount(truth[mask],minlength=10);correct=np.bincount(truth[mask&(truth==pred)],minlength=10);predicted=np.bincount(pred[mask],minlength=10);active=selected>0;probs=predicted[predicted>0]/mask.sum()
                    values=dict(coverage=100*mask.mean(),accuracy=100*correct.sum()/selected.sum(),macro_accepted_recall=10*np.sum(correct/totals),selected_class_macro_accuracy=100*np.mean(correct[active]/selected[active]),represented_true_classes=int(active.sum()),predicted_classes=int(np.count_nonzero(predicted)),effective_predicted_classes=float(np.prod(probs**(-probs))),minimum_class_retention=100*np.min(selected/totals),jaccard_certificate_gated=jacc,identical_sets=bool(np.array_equal(cert,gated)))
                    for key,value in values.items():
                        if key=='identical_sets':assert (r[key]=='True')==value
                        else:assert abs(float(r[key])-value)<1e-10,(name,ratio,selector,key,r[key],value)
                    for c in range(10):
                        cc=[r for r in classes if r['dataset']==dataset and int(r['seed'])==seed and float(r['width'])==ratio and r['selector']==selector and int(r['truth_class'])==c];assert len(cc)==1
                        assert int(cc[0]['total'])==totals[c] and int(cc[0]['selected'])==selected[c] and int(cc[0]['correct'])==correct[c]
                        classchecked+=1
                    generated.append(dict(dataset=dataset,seed=seed,width=ratio,selector=selector,**values));checked+=1
                if dataset=='mnist' and ratio==1:
                    assert np.all(pred==1) and np.array_equal(cert,gated)
            print(name,'PASS',flush=True)
    for r in summaries:
        rr=[x for x in generated if x['dataset']==r['dataset'] and x['width']==float(r['width']) and x['selector']==r['selector']];assert len(rr)==5
        for key in list(generated[0])[4:]:
            v=np.array([x[key] for x in rr],dtype=float)
            assert abs(float(r[key+'_mean'])-v.mean())<1e-10
            assert abs(float(r[key+'_sd'])-v.std(ddof=1))<1e-10
    for p in RESULT.glob('selection_diagnostics_*.csv'):hashes[str(p.relative_to(ROOT))]=hashlib.sha256(p.read_bytes()).hexdigest()
    report=dict(status='PASS',source='Independent raw-image and archived-weight reconstruction; no imports from analysis runner',settings=20,selector_rows=checked,class_rows=classchecked,summary_rows=8,prediction_labels=prediction_labels,new_fits=0,comparison='Every metric and class count matches; mean and sample SD independently recomputed',mnist_t_sC_class_one_and_identical_sets=True,script_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),input_sha256=hashes,elapsed_seconds=time.perf_counter()-started)
    (HERE/'composition_verification.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({k:v for k,v in report.items() if k!='input_sha256'},indent=2))

if __name__=='__main__':
    with threadpool_limits(1):main()
