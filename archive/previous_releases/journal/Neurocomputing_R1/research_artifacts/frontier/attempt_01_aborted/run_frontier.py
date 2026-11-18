#!/usr/bin/env python3
"""Predeclared supplementary grid study; frozen functions and label-free selection."""
import csv,hashlib,importlib.util,json,platform,sys,time
from datetime import datetime,timezone
from pathlib import Path
import numpy as np
from scipy.linalg import svd
from scipy.spatial.distance import cdist
from threadpoolctl import threadpool_limits,threadpool_info

HERE=Path(__file__).resolve().parent
BASE=HERE.parent/'baseline'
EXP=BASE/'work/v2/experiment'
sys.path.insert(0,str(EXP))
import certificate as cert
import run_experiment as old

def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def js(p,x):Path(p).write_text(json.dumps(x,indent=2,allow_nan=False)+'\n')
def csvwrite(p,rows):
    if not rows:return
    with Path(p).open('w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(dict.fromkeys(k for r in rows for k in r)));w.writeheader();w.writerows(rows)
def utc():return datetime.now(timezone.utc).isoformat()

def main():
    freeze=json.loads((HERE/'FREEZE.json').read_text())
    assert sha(HERE/'protocol.json')==freeze['protocol_sha256']
    assert sha(__file__)==freeze['runner_sha256']
    assert sha(EXP/'certificate.py')==freeze['certificate_sha256']
    for rel,h in freeze['input_sha256'].items():assert sha(BASE/rel)==h,rel
    out=HERE/'results';out.mkdir(exist_ok=False)
    js(out/'environment.json',dict(started_utc=utc(),python=sys.version,platform=platform.platform(),numpy=np.__version__,threads=threadpool_info(),freeze=freeze))
    p=json.loads((EXP/'protocol.json').read_text());ratios=np.geomspace(1/32,1/4,65);lows=[0,1,100]
    coverage=[];diagnostics=[];timings=[];groups=[];targets=[('any',None),('50pct',.5),('90pct',.9)]
    start=time.perf_counter()
    with threadpool_limits(1):
        for dataset in p['datasets']:
            images,yall,query_images,query_ids=old.data_load(dataset,p);Xq=old.flatten(query_images)
            for seed in p['seeds']:
                for K in p['prototype_budgets']:
                    t0=time.perf_counter();name=f'{dataset}_seed{seed}_K{K}';orig=EXP/'results'/name/'predictions_before_labels.npz'
                    with np.load(orig) as z:
                        tids=z['train_ids'];rows=z['center_rows'];yc=z['center_labels'];nn=z['nearest_prototype'];scale=float(z['width_upper_bounds'][1]*16);frozen_masks=z['certificate_masks'];assert np.array_equal(query_ids,z['query_ids']);assert np.array_equal(tids[rows],z['center_ids'])
                    X=old.flatten(images[tids]);y=yall[tids];Y=np.eye(10)[y];Yc=Y[rows];assert np.array_equal(y[rows],yc)
                    Dt=cdist(X,X[rows],'sqeuclidean');Dq=cdist(Xq,X[rows],'sqeuclidean');widths=ratios*scale;n=len(Dq)
                    masks=np.zeros((65,3,3,n),bool);bounds=np.zeros((65,3,3,10,10));last=np.full((3,3,n),-1,np.int16)
                    for wi,t in enumerate(widths):
                        H=np.exp(-Dt/(2*t*t));terms=cert.training_terms(H,Y,rows)
                        diagnostics.append(dict(dataset=dataset,seed=seed,K=K,grid_index=wi,sigma=float(t),sigma_over_sC=float(ratios[wi]),beta=terms['beta'],mu=terms['mu'],eta=terms['eta']))
                        for li,lo in enumerate(lows):
                            b,app=cert.constants(terms,lo);cm,ref,gap,unique=cert.query_certificate(Dq,Yc,t,b,p['strict_guard'],p['nearest_tie_relative']);assert np.array_equal(ref,nn)
                            if wi:assert np.all(~cm|masks[wi-1,li]),'Nonmonotone certificate mask'
                            assert np.all(~cm[1]|cm[0]) and np.all(~cm[2]|cm[1])
                            masks[wi,li]=cm;bounds[wi,li]=b;last[li][cm]=wi
                            for mi,method in enumerate(cert.METHODS):coverage.append(dict(dataset=dataset,seed=seed,K=K,grid_index=wi,sigma=float(t),sigma_over_sC=float(ratios[wi]),lambda_floor=lo,method=method,n=n,certified=int(cm[mi].sum()),coverage=float(cm[mi].mean()),applicable=app))
                        for gi,fi in [(int(np.argmin(abs(ratios-.0625))),1),(int(np.argmin(abs(ratios-.125))),2),(64,3)]:
                            if wi==gi:assert np.array_equal(masks[wi],frozen_masks[fi]),'Frozen shared-width mask mismatch'
                    chosen=[]
                    for li,lo in enumerate(lows):
                        counts=masks[:,li,0].sum(axis=1)
                        for target,fraction in targets:
                            valid=np.flatnonzero(counts>=int(np.ceil(fraction*n))) if fraction is not None else np.flatnonzero(counts>0)
                            chosen.append(dict(lambda_floor=lo,target=target,grid_index=int(valid[-1]) if len(valid) else -1))
                    fit_indices=sorted(set(a['grid_index'] for a in chosen if a['grid_index']>=0));pred=np.zeros((len(fit_indices),3,n),np.int8);weights=np.zeros((len(fit_indices),3,K,10));ranks=[]
                    for fi,wi in enumerate(fit_indices):
                        t=widths[wi];H=np.exp(-Dt/(2*t*t));H[rows,np.arange(K)]=1;u,s,vt=svd(H,full_matrices=False,check_finite=False);uty=u.T@Y;ranks.append(int(np.sum(s>max(len(X),len(s))*np.finfo(float).eps*s[0])))
                        for li,lo in enumerate(lows):
                            W=old.fit_from_factor(s,vt,uty,lo,len(X));weights[fi,li]=W;pred[fi,li]=np.argmax(cert.query_features(Dq,t)@W,axis=1)
                            assert not np.any(masks[wi,li]&(pred[fi,li]!=nn)[None,:]),'Certified endpoint disagreement'
                    group=out/name;group.mkdir()
                    np.savez_compressed(group/'frontiers_before_labels.npz',ratios=ratios,widths=widths,lambda_floors=lows,methods=cert.METHODS,certificate_masks=masks,pair_constants=bounds,last_certified_grid_index=last,next_failed_grid_index=np.where(last<64,last+1,-1),left_censored=last<0,right_censored=last==64,query_ids=query_ids,nearest_prototype=nn,train_ids=tids,center_rows=rows,center_ids=tids[rows],center_labels=yc,fit_grid_indices=fit_indices,predictions=pred,weights=weights,numerical_ranks=ranks)
                    js(group/'chosen_endpoints_before_labels.json',chosen);files={f.name:sha(f) for f in group.iterdir() if f.is_file()};js(group/'PREDICTIONS_FROZEN.json',dict(frozen_utc=utc(),heldout_truth_used=False,files=files,input_archive_sha256=sha(orig)))
                    groups.append((dataset,seed,K,group));timings.append(dict(dataset=dataset,seed=seed,K=K,seconds=time.perf_counter()-t0,selected_distinct_widths=len(fit_indices)));csvwrite(out/'progress.csv',timings);print(json.dumps(timings[-1]),flush=True)
        js(out/'ALL_PREDICTIONS_FROZEN.json',dict(frozen_utc=utc(),heldout_truth_used=False,groups=[dict(dataset=d,seed=s,K=k,freeze_sha256=sha(g/'PREDICTIONS_FROZEN.json')) for d,s,k,g in groups]))
        # Evaluation targets are indexed only after every supplementary prediction archive is frozen.
        endpoints=[];frontiers=[]
        for dataset,seed,K,group in groups:
            yy=np.load(EXP/'results'/f'{dataset}_evaluation_labels.npy')
            with np.load(group/'frontiers_before_labels.npz') as z:
                masks=z['certificate_masks'];last=z['last_certified_grid_index'];nn=z['nearest_prototype'];widths=z['widths'];fit_indices=z['fit_grid_indices'];pred=z['predictions'];n=len(yy)
                for li,lo in enumerate(lows):
                    for mi,method in enumerate(cert.METHODS):
                        idx=last[li,mi];inside=idx>=0;values=ratios[idx[inside]]
                        frontiers.append(dict(dataset=dataset,seed=seed,K=K,lambda_floor=lo,method=method,n=n,left_censored=int((idx<0).sum()),right_censored=int((idx==64).sum()),minimum_last_certified_ratio=float(values.min()) if len(values) else None,q10_last_certified_ratio=float(np.quantile(values,.1)) if len(values) else None,median_last_certified_ratio=float(np.median(values)) if len(values) else None,q90_last_certified_ratio=float(np.quantile(values,.9)) if len(values) else None,maximum_last_certified_ratio=float(values.max()) if len(values) else None))
                with np.load(EXP/'results'/group.name/'predictions_before_labels.npz') as oldz:
                    oldpred=oldz['predictions'];oldws=oldz['probe_widths'];oldl=oldz['probe_penalties']
                    for choice in json.loads((group/'chosen_endpoints_before_labels.json').read_text()):
                        lo=choice['lambda_floor'];li=lows.index(lo);wi=choice['grid_index'];base=dict(dataset=dataset,seed=seed,K=K,lambda_floor=lo,target=choice['target'],available=wi>=0,n=n)
                        if wi<0:endpoints.append(base);continue
                        fi=list(fit_indices).index(wi);pr=pred[fi,li];cm=masks[wi,li,0];oldli=int(np.flatnonzero(oldl==lo)[0]);oldacc=(oldpred[:,oldli]==yy).mean(axis=1);best=int(np.argmax(oldacc));acc=float(np.mean(pr==yy))
                        endpoints.append(dict(base,grid_index=wi,sigma=float(widths[wi]),sigma_over_sC=float(ratios[wi]),certified=int(cm.sum()),coverage=float(cm.mean()),accuracy=acc,nearest_accuracy=float(np.mean(nn==yy)),nearest_agreement=float(np.mean(pr==nn)),certified_accuracy=float(np.mean(pr[cm]==yy[cm])),certified_disagreements=int(np.sum(cm&(pr!=nn))),best_frozen_sampled_accuracy=float(oldacc[best]),best_frozen_sampled_sigma=float(oldws[best]),best_frozen_sampled_ratio=float(oldws[best]/(widths[0]/ratios[0])),accuracy_loss_vs_best_frozen_pp=float(100*(oldacc[best]-acc))))
        csvwrite(out/'grid_coverage.csv',coverage);csvwrite(out/'training_diagnostics.csv',diagnostics);csvwrite(out/'query_frontier_summary.csv',frontiers);csvwrite(out/'endpoint_metrics.csv',endpoints)
        js(out/'COMPLETE.json',dict(completed_utc=utc(),groups=len(groups),grid_widths=65,coverage_rows=len(coverage),endpoint_rows=len(endpoints),runtime_seconds=time.perf_counter()-start,certified_endpoint_disagreements=sum(e.get('certified_disagreements',0) for e in endpoints),numeric_nesting='PASS',frozen_shared_width_masks='PASS'))
        js(out/'MANIFEST_SHA256.json',{str(f.relative_to(out)):sha(f) for f in sorted(out.rglob('*')) if f.is_file() and f.name!='MANIFEST_SHA256.json'})
    print((out/'COMPLETE.json').read_text(),flush=True)
if __name__=='__main__':main()
