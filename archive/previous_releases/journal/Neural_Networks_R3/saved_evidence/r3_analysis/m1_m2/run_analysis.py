#!/usr/bin/env python3
"""R3 M1/M2 analysis from immutable R2 arrays; no new model fitting."""
import csv, gzip, hashlib, json, platform, sys, time
from pathlib import Path
import numpy as np
from scipy.io import loadmat
from scipy.spatial.distance import cdist
from threadpoolctl import threadpool_limits

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
EVID=ROOT/'evidence'
BASE=EVID/'baseline/evidence/baseline'
EXP=BASE/'work/v2/experiment/results'
FRONT=EVID/'baseline/evidence/frontier/results'
DIAG=EVID/'new_analysis/limit_diagnostic'
PROTOCOL='22a65a03a996dea12278896442ec85ccce09f65ee372b4970fb4e2391918d9d9'

def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def js(p,x): p.write_text(json.dumps(x,indent=2,allow_nan=False)+'\n')
def csvwrite(p,rows):
    with p.open('w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
def idx(p):
    b=gzip.decompress(p.read_bytes());return np.frombuffer(b,np.uint8,offset=16).reshape(-1,28,28)
def flatten(a): return a.transpose(0,2,1).reshape(len(a),-1).astype(float)/255
def strict_scores(r,W,nn):
    scores=r@W; pred=scores.argmax(1).astype(np.int8)
    ns=scores[np.arange(len(nn)),nn].copy();scores[np.arange(len(nn)),nn]=-np.inf
    cs=scores.max(1);return cs-ns>1e-10*(1+abs(cs)+abs(ns)),pred

def main():
    assert sha(HERE/'protocol.json')==PROTOCOL
    out=HERE/'results';out.mkdir(exist_ok=True)
    start=time.perf_counter();m1=[];m2=[];valrows=[];groupinfo=[];inputs={};guardchecks=0;violations=0;crosscheck=0.;fits=0
    frozen_rows={(r['dataset'],int(r['seed']),int(r['width_index']),int(r['lambda_floor'])):r for r in csv.DictReader((DIAG/'original7_guarded/rectangles.csv').open())}
    with threadpool_limits(1):
      for dataset in ['mnist','fashion_mnist']:
        if dataset=='mnist':
            p=BASE/'repository/Code/MNIST_train.mat';d=loadmat(p);images=d['imagestrain'].transpose(2,0,1);labels=d['labelstrain'].ravel().astype(int)
            qimages=images[np.load(BASE/'work/v2/design/reserved_training_ids.npy')]
        else:
            folder=BASE/'work/v2/data/fashion_mnist';images=idx(folder/'train-images-idx3-ubyte.gz');qimages=idx(folder/'t10k-images-idx3-ubyte.gz');labels=np.frombuffer(gzip.decompress((folder/'train-labels-idx1-ubyte.gz').read_bytes()),np.uint8,offset=8).astype(int)
        Xq=flatten(qimages)
        for seed in [11,22,33,44,55]:
            gstart=time.perf_counter();name=f'{dataset}_seed{seed}_K100';p=EXP/name/'predictions_before_labels.npz';inputs[str(p.relative_to(ROOT))]=sha(p)
            with np.load(p) as z:
                train=z['train_ids'];valid=z['validation_ids'];center=z['center_ids'];rows=z['center_rows'];nn=z['nearest_prototype'];widths=z['width_upper_bounds'];pw=z['probe_widths'];pl=z['probe_penalties'];weights=z['weights'];ranks=z['numerical_ranks'];oldpred=z['predictions'];cert=z['certificate_masks'][:,:,0];floors=z['lambda_lower_bounds'];qids=z['query_ids']
            assert len(set(train)&set(valid))==0
            if dataset=='mnist': assert len(set(valid)&set(qids))==0
            C=flatten(images[center]);X=flatten(images[train]);Xv=flatten(images[valid]);Y=np.eye(10)[labels[train]]
            Dt=cdist(X,C,'sqeuclidean');Dq=cdist(Xq,C,'sqeuclidean');Dq-=Dq.min(1,keepdims=True);Dv=cdist(Xv,C,'sqeuclidean');Dv-=Dv.min(1,keepdims=True)
            n=len(nn);scale=widths[1]*16.;valpred=np.empty((len(pw),len(pl),len(valid)),np.int8);valacc=np.empty((len(pw),len(pl)));f0=[];f1=[];pred_mismatch=0
            for wi,w in enumerate(pw):
                rq=np.exp(-Dq/(2*w*w));rv=np.exp(-Dv/(2*w*w))
                for li,lam in enumerate(pl):
                    vpred=(rv@weights[wi,li]).argmax(1);valpred[wi,li]=vpred;valacc[wi,li]=np.mean(vpred==labels[valid])
                    mask,pred=strict_scores(rq,weights[wi,li],nn);pred_mismatch+=np.count_nonzero(pred!=oldpred[wi,li])
                    if lam==0 and ranks[wi]<100: mask[:]=False
                    f0.append((float(w),float(lam),mask,'original'))
            bestval=valacc.max();competitive=valacc>=.95*bestval;globalmax=float(np.max(np.broadcast_to(pl,valacc.shape)[competitive]))
            for wi,w in enumerate(pw):
                for li,lam in enumerate(pl):
                    valrows.append(dict(dataset=dataset,seed=seed,sigma=float(w),sigma_over_sC=float(w/scale),penalty=int(lam),validation_n=len(valid),validation_accuracy_pct=float(100*valacc[wi,li]),competitive=bool(competitive[wi,li]),group_best_validation_accuracy_pct=float(100*bestval)))
            f1.extend(f0)
            p=FRONT/name/'frontiers_before_labels.npz';inputs[str(p.relative_to(ROOT))]=sha(p)
            with np.load(p) as z:
                fw=z['widths'][z['fit_grid_indices']];fl=z['lambda_floors'];ww=z['weights'];fr=z['numerical_ranks'];fp=z['predictions']
            for wi,w in enumerate(fw):
                rq=np.exp(-Dq/(2*w*w))
                for li,lam in enumerate(fl):
                    mask,pred=strict_scores(rq,ww[wi,li],nn);pred_mismatch+=np.count_nonzero(pred!=fp[wi,li])
                    if lam==0 and fr[wi]<100: mask[:]=False
                    f1.append((float(w),float(lam),mask,'frontier'))
            p=DIAG/'local_tail_validation'/f'{name}.npz';inputs[str(p.relative_to(ROOT))]=sha(p)
            with np.load(p) as z,np.load(DIAG/'local_tail'/f'{name}.npz') as tail:
                for ri,ratio in enumerate([.5,1.]):
                    op=float(np.linalg.eigvalsh(tail[f'case{2*ri}_A_t'])[-1])
                    for li,mult in enumerate([10,100]):
                        for si,frac in enumerate([.95,.99,1.]):
                            w=scale*ratio*frac;mask,pred=strict_scores(np.exp(-Dq/(2*w*w)),z[f't{ri}_weights'][li,si],nn)
                            pred_mismatch+=np.count_nonzero(pred!=z[f't{ri}_predictions'][li,si])
                            f1.append((float(w),float(mult*op),mask,'local_tail'))
            assert pred_mismatch==0,(name,pred_mismatch)
            p=DIAG/'original7_guarded'/f'{name}.npz';inputs[str(p.relative_to(ROOT))]=sha(p)
            with np.load(p) as z:
                ol=z['endpoint_obstruction'];oprefix=z['prefix_obstruction'];ow=z['widths'];oldfinite=z['finite_probe_obstruction'];oldB=z['HtY']
            p=DIAG/'dense67_guarded'/f'{name}.npz';inputs[str(p.relative_to(ROOT))]=sha(p)
            with np.load(p) as z: dl=z['endpoint_obstruction'];dw=z['widths']
            threshold=np.full((len(widths),n),np.inf);normth=threshold.copy();bestclass=np.full((len(widths),n),-1,np.int8);ops=[];competitive_max=[]
            union_limit=[];finite_orig=[];finite_all=[]
            for wi,w in enumerate(widths):
                H=np.exp(-Dt/(2*w*w));H[rows,np.arange(100)]=1.;A=H.T@H;Z=H.T@Y;crosscheck=max(crosscheck,float(abs(Z-oldB[wi]).max()));eig,U=np.linalg.eigh(A);op=float(eig[-1]);ops.append(op)
                r=np.exp(-Dq/(2*w*w));rn=np.linalg.norm(r,axis=1);scores=r@Z;ns=scores[np.arange(n),nn];delta=scores-ns[:,None];sg=1e-10*(1+abs(scores)+abs(ns[:,None]));comp=delta>sg;comp[np.arange(n),nn]=False
                norms=np.linalg.norm((A@Z)[:,None,:]-(A@Z)[:,:,None],axis=0)
                candidates=np.full((n,10),np.inf);np.divide(rn[:,None]*norms[nn],delta,out=candidates,where=comp)
                th=np.min(candidates,axis=1);finite=np.isfinite(th);bc=candidates.argmin(1);bc[~finite]=-1;threshold[wi]=th;normth[wi]=th/op;bestclass[wi]=bc
                assert np.array_equal(finite,ol[wi])
                match=np.flatnonzero(np.isclose(pw,w,rtol=1e-13,atol=0));assert len(match)==1
                cm=pl[competitive[match[0]]];maxlam=float(cm.max()) if len(cm) else None;competitive_max.append(np.nan if maxlam is None else maxlam)
                checks=np.flatnonzero(finite);lamb=1.001*th[checks];rU=r[checks]@U;UZ=U.T@Z
                vv=(UZ[:,bc[checks]]-UZ[:,nn[checks]]).T
                diff=np.sum(rU*vv/(1+eig[None,:]/lamb[:,None]),axis=1)
                failures=int(np.count_nonzero(diff<=0));violations+=failures;guardchecks+=len(checks)
                row=dict(dataset=dataset,seed=seed,width_index=wi,sigma=float(w),sigma_over_sC=float(w/scale),n=n,operator_norm=op,strict_limit_queries=int(finite.sum()),strict_limit_pct=float(finite.mean()*100),validation_best_pct=float(bestval*100),competitive_max_penalty_same_width=maxlam,competitive_max_normalized_same_width=(maxlam/op if maxlam is not None else None),competitive_max_penalty_any_width=globalmax,bound_within_same_width_competitive=int(np.sum(th<maxlam)) if maxlam is not None else None,bound_within_any_width_max=int(np.sum(th<globalmax)),verified_finite_reversals=len(checks),verification_failures=failures)
                for q in [0,.25,.5,.75,.9,1]:row['normalized_threshold_q'+str(q)]=float(np.quantile(th[finite]/op,q)) if finite.any() else None
                m1.append(row)
                lim=oprefix[wi]|np.any(dl[dw<=w*(1+1e-14)],axis=0);union_limit.append(lim)
                f0all=[];f1all=[]
                for li,floor in enumerate(floors):
                    def unions(records):
                        masks=[m for ww,ll,m,_ in records if ww<=w*(1+1e-14) and ll>=floor]
                        return np.any(masks,axis=0) if masks else np.zeros(n,bool)
                    fo=unions(f0);fa=unions(f1);f0all.append(fo);f1all.append(fa);assert np.array_equal(fo,oldfinite[wi,li]);assert not np.any(cert[wi,li]&(lim|fa))
                    r2limit=oprefix[wi]
                    sets=dict(endpoint_limit=ol[wi],original_limit_prefix=r2limit,dense_limit_prefix=lim,original_finite=fo,all_archived_finite=fa,limit_and_original_finite=lim&fo,limit_only_vs_original=lim&~fo,original_finite_only_vs_limit=fo&~lim,limit_and_all_finite=lim&fa,limit_only_vs_all=lim&~fa,all_finite_only_vs_limit=fa&~lim,expanded_finite_unique=fa&~fo,endpoint_limit_plus_original_finite=ol[wi]|fo,combined_full=lim|fa,unresolved_full=~cert[wi,li]&~(lim|fa),certified=cert[wi,li],r2_union=r2limit|fo,r2_limit_only_vs_original=r2limit&~fo,limit_unique_after_endpoint_zero=np.zeros(n,bool))
                    sets['r2_limit_only_vs_all']=r2limit&~fa
                    sets['all_finite_only_vs_r2_limit']=fa&~r2limit
                    sets['r2_limit_and_all_finite']=r2limit&fa
                    sets['r2_limit_and_original_finite']=r2limit&fo
                    zero=f0[6*int(match[0])][2];sets['limit_unique_after_endpoint_zero']=ol[wi]&~zero
                    rr=dict(dataset=dataset,seed=seed,width_index=wi,sigma_over_sC=float(w/scale),penalty_floor=int(floor),n=n)
                    rr.update({k:int(v.sum()) for k,v in sets.items()})
                    frozen=frozen_rows[(dataset,seed,wi,int(floor))]
                    assert rr['r2_union']==int(frozen['combined_excluded'])
                    assert rr['certified']==int(frozen['certified'])
                    m2.append(rr)
                finite_orig.append(f0all);finite_all.append(f1all)
            np.savez_compressed(out/f'{name}.npz',threshold=threshold,normalized_threshold=normth,best_competing_class=bestclass,operator_norm=np.array(ops),competitive_max_same_width=np.array(competitive_max),validation_predictions=valpred,validation_accuracy=valacc,validation_ids=valid,validation_truth=labels[valid],widths=widths,probe_widths=pw,probe_penalties=pl,nearest_prototype=nn,query_ids=qids,original_limit=ol,original_limit_prefix=oprefix,dense_limit_prefix=np.array(union_limit),finite_original=np.array(finite_orig),finite_all_archived=np.array(finite_all),certified=cert)
            groupinfo.append(dict(group=name,seconds=time.perf_counter()-gstart,finite_original_pairs=len(f0),finite_all_archived_pairs=len(f1),prediction_mismatch=int(pred_mismatch)));print(json.dumps(groupinfo[-1]),flush=True)
    assert violations==0
    csvwrite(out/'m1_thresholds_per_seed.csv',m1);csvwrite(out/'m2_overlap_per_seed.csv',m2);csvwrite(out/'validation_reference_per_pair.csv',valrows)
    summaries=[]
    for ds in ['mnist','fashion_mnist']:
      for wi in range(7):
        rr=[r for r in m1 if r['dataset']==ds and r['width_index']==wi];row=dict(dataset=ds,width_index=wi,sigma_over_sC_mean=float(np.mean([r['sigma_over_sC'] for r in rr])),seeds=5,n_per_seed=rr[0]['n'],seeds_with_competitive_readout=sum(r['competitive_max_penalty_same_width'] is not None for r in rr),bound_within_competitive_total=sum(r['bound_within_same_width_competitive'] or 0 for r in rr),eligible_strict_limit_total=sum(r['strict_limit_queries'] for r in rr if r['competitive_max_penalty_same_width'] is not None))
        for f in ['strict_limit_pct','normalized_threshold_q0.5','normalized_threshold_q0.9','normalized_threshold_q1']:
            vals=[r[f] for r in rr if r[f] is not None];row[f+'_mean']=float(np.mean(vals)) if vals else None;row[f+'_sd']=float(np.std(vals,ddof=1)) if len(vals)>1 else None
        summaries.append(row)
    csvwrite(out/'m1_summary.csv',summaries)
    summaries=[];metrics=list(m2[0])[6:]
    for ds in ['mnist','fashion_mnist']:
      for wi in range(7):
       for fl in [0,1,100]:
        rr=[r for r in m2 if r['dataset']==ds and r['width_index']==wi and r['penalty_floor']==fl];row=dict(dataset=ds,width_index=wi,sigma_over_sC_mean=float(np.mean([r['sigma_over_sC'] for r in rr])),penalty_floor=fl,seeds=5,n_per_seed=rr[0]['n'])
        for m in metrics:
            v=np.array([r[m]/r['n']*100 for r in rr]);row[m+'_mean_pct']=float(v.mean());row[m+'_sd_pp']=float(v.std(ddof=1))
        summaries.append(row)
    csvwrite(out/'m2_summary.csv',summaries)
    js(out/'COMPLETE.json',dict(protocol_sha256=PROTOCOL,runner_sha256=sha(Path(__file__)),runtime_seconds=time.perf_counter()-start,new_readout_fits=0,archived_validation_evaluations=960,groups=groupinfo,finite_reversal_checks=guardchecks,finite_reversal_failures=violations,maximum_HtY_absolute_error=crosscheck,inputs=inputs,python=sys.version,numpy=np.__version__,platform=platform.platform()))
    js(out/'SHA256_MANIFEST.json',{p.name:sha(p) for p in sorted(out.iterdir()) if p.name!='SHA256_MANIFEST.json'})

if __name__=='__main__':main()
