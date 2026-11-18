#!/usr/bin/env python3
import json,time
from pathlib import Path
import numpy as np
from scipy.io import loadmat
from scipy.spatial.distance import cdist
from threadpoolctl import threadpool_limits
from run_limit_diagnostic import HERE,ROOT,BASE,EXP,idx,flatten,sha,js,csvwrite

def main():
    out=HERE/'local_tail_validation';out.mkdir(exist_ok=False);start=time.perf_counter();allrows=[];certrows=[];checks=0;viols=0;fits=0
    with threadpool_limits(1):
        for d in ['mnist','fashion_mnist']:
            if d=='mnist':
                images=loadmat(BASE/'repository/Code/MNIST_train.mat',variable_names=['imagestrain'])['imagestrain'].transpose(2,0,1);qimages=images[np.load(BASE/'work/v2/design/reserved_training_ids.npy')]
            else:
                folder=BASE/'work/v2/data/fashion_mnist';images=idx(folder/'train-images-idx3-ubyte.gz');qimages=idx(folder/'t10k-images-idx3-ubyte.gz')
            Xq=flatten(qimages);truth=np.load(EXP/f'{d}_evaluation_labels.npy')
            for seed in [11,22,33,44,55]:
                name=f'{d}_seed{seed}_K100'
                with np.load(EXP/name/'predictions_before_labels.npz') as z:C=flatten(images[z['center_ids']]);nn=z['nearest_prototype'];scale=float(z['width_upper_bounds'][1]*16)
                D=cdist(Xq,C,'sqeuclidean');D-=D.min(axis=1,keepdims=True);n=len(nn);saved={}
                with np.load(HERE/'local_tail'/f'{name}.npz') as z:
                    for ri,ratio in enumerate([.5,1.]):
                        ci=2*ri;At=z[f'case{ci}_A_t'];Bt=z[f'case{ci}_B_t'];op=float(np.linalg.eigvalsh(At)[-1]);t=ratio*scale;pred=np.empty((2,3,n),np.int8);weights=np.empty((2,3,100,10))
                        for si,frac in enumerate([.95,.99,1.]):
                            if frac==1.:A=At;B=Bt
                            else:
                                c=ci+(0 if frac==.99 else 1);A=z[f'case{c}_A_s'];B=z[f'case{c}_B_s']
                            r=np.exp(-D/(2*(frac*t)**2))
                            for li,mult in enumerate([10,100]):
                                W=np.linalg.solve(A+mult*op*np.eye(100),B);weights[li,si]=W;pred[li,si]=(r@W).argmax(axis=1);fits+=1
                        for li,mult in enumerate([10,100]):
                            p=pred[li,2];allrows.append(dict(dataset=d,seed=seed,K=100,n=n,t_over_sC=ratio,lambda_over_At_operator=mult,lambda_value=float(mult*op),readout_accuracy_pct=float(np.mean(p==truth)*100),nearest_agreement_pct=float(np.mean(p==nn)*100),nearest_accuracy_pct=float(np.mean(nn==truth)*100)))
                            for bi,frac in enumerate([.99,.95]):
                                threshold=z[f'case{ci+bi}_threshold'];mask=threshold<=mult*op;inside=[j for j,q in enumerate([.95,.99,1.]) if q>=frac];bad=sum(int(np.sum(mask&(pred[li,j]!=nn))) for j in inside);nc=int(mask.sum());cc=int(np.sum(mask&(p==truth)));checks+=nc*len(inside);viols+=bad
                                certrows.append(dict(dataset=d,seed=seed,K=100,n=n,t_over_sC=ratio,s_over_t=frac,lambda_over_At_operator=mult,certified=nc,coverage_pct=float(nc/n*100),certified_true_correct=cc,certified_true_accuracy_pct=float(cc/nc*100) if nc else None,sampled_widths=len(inside),certified_query_parameter_checks=nc*len(inside),disagreements=bad))
                        saved[f't{ri}_predictions']=pred;saved[f't{ri}_weights']=weights
                np.savez_compressed(out/f'{name}.npz',nearest_prototype=nn,**saved)
    assert viols==0;csvwrite(out/'all_query_per_seed.csv',allrows);csvwrite(out/'certified_per_seed.csv',certrows)
    summaries=[]
    for d in ['mnist','fashion_mnist']:
        for r in [.5,1.]:
            for mult in [10,100]:
                rows=[a for a in allrows if a['dataset']==d and a['t_over_sC']==r and a['lambda_over_At_operator']==mult];z=dict(dataset=d,t_over_sC=r,lambda_over_At_operator=mult)
                for field in ['readout_accuracy_pct','nearest_agreement_pct','nearest_accuracy_pct']:
                    v=np.array([a[field] for a in rows]);z[field+'_mean']=float(v.mean());z[field+'_sd_pp']=float(v.std(ddof=1))
                summaries.append(z)
    csvwrite(out/'all_query_summary.csv',summaries);summaries=[]
    for d in ['mnist','fashion_mnist']:
        for r in [.5,1.]:
            for frac in [.99,.95]:
                for mult in [10,100]:
                    rows=[a for a in certrows if a['dataset']==d and a['t_over_sC']==r and a['s_over_t']==frac and a['lambda_over_At_operator']==mult];z=dict(dataset=d,t_over_sC=r,s_over_t=frac,lambda_over_At_operator=mult)
                    for field in ['coverage_pct','certified_true_accuracy_pct']:
                        v=np.array([a[field] for a in rows if a[field] is not None]);z[field+'_mean']=float(v.mean()) if len(v) else None;z[field+'_sd_pp']=float(v.std(ddof=1)) if len(v)>1 else None
                    z['zero_coverage_seeds']=sum(a['certified']==0 for a in rows);z['disagreements']=sum(a['disagreements'] for a in rows);summaries.append(z)
    csvwrite(out/'certified_summary.csv',summaries);js(out/'COMPLETE.json',dict(runtime_seconds=time.perf_counter()-start,readout_fits=fits,certified_sampled_checks=checks,certified_sampled_disagreements=viols,protocol_sha256=sha(HERE/'local_tail_validation_protocol.json'),runner_sha256=sha(Path(__file__))))
    js(out/'MANIFEST_SHA256.json',{p.name:sha(p) for p in out.iterdir() if p.is_file()});print(json.dumps(dict(fits=fits,checks=checks,violations=viols,seconds=time.perf_counter()-start)))
if __name__=='__main__':main()
