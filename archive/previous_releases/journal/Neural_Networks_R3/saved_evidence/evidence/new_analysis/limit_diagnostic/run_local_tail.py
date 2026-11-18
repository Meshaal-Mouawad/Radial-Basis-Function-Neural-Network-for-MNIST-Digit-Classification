#!/usr/bin/env python3
"""Fit-free local bandwidth / large-ridge certificate diagnostic."""
import json,csv,time,hashlib
from pathlib import Path
from datetime import datetime,timezone
import numpy as np
from scipy.io import loadmat
from scipy.spatial.distance import cdist
from threadpoolctl import threadpool_limits
from run_limit_diagnostic import HERE,ROOT,BASE,EXP,idx,flatten,sha,js,csvwrite

def main():
    p=json.loads((HERE/'local_tail_protocol.json').read_text());out=HERE/'local_tail';out.mkdir(exist_ok=False)
    start=time.perf_counter();rec=[];timings=[]
    with threadpool_limits(1):
        for dataset in ['mnist','fashion_mnist']:
            if dataset=='mnist':
                z=loadmat(BASE/'repository/Code/MNIST_train.mat');images=z['imagestrain'].transpose(2,0,1);labels=z['labelstrain'].ravel().astype(int);qimages=images[np.load(BASE/'work/v2/design/reserved_training_ids.npy')]
            else:
                import gzip
                folder=BASE/'work/v2/data/fashion_mnist';images=idx(folder/'train-images-idx3-ubyte.gz');qimages=idx(folder/'t10k-images-idx3-ubyte.gz');labels=np.frombuffer(gzip.decompress((folder/'train-labels-idx1-ubyte.gz').read_bytes()),np.uint8,offset=8).astype(int)
            Xq=flatten(qimages)
            for seed in [11,22,33,44,55]:
                t0=time.perf_counter();name=f'{dataset}_seed{seed}_K100'
                with np.load(EXP/name/'predictions_before_labels.npz') as z:train=z['train_ids'];rows=z['center_rows'];nn=z['nearest_prototype'];scale=float(z['width_upper_bounds'][1]*16);qids=z['query_ids']
                X=flatten(images[train]);Y=np.eye(10)[labels[train]];C=X[rows];Dt=cdist(X,C,'sqeuclidean');Dq=cdist(Xq,C,'sqeuclidean');Dq-=Dq.min(axis=1,keepdims=True);n=len(nn)
                all_arrays={};case=0
                for ratio in [.5,1.]:
                    t=ratio*scale;Ht=np.exp(-Dt/(2*t*t));Ht[rows,np.arange(100)]=1;At=Ht.T@Ht;Bt=Ht.T@Y;rt=np.exp(-Dq/(2*t*t));vt=rt@Bt;rn=np.linalg.norm(rt,axis=1);op=float(np.linalg.eigvalsh(At)[-1]);trace=float(np.trace(At))
                    for frac in [.99,.95]:
                        s=frac*t;Hs=np.exp(-Dt/(2*s*s));Hs[rows,np.arange(100)]=1;As=Hs.T@Hs;Bs=Hs.T@Y;rs=np.exp(-Dq/(2*s*s));vs=rs@Bs;vsa=vs[np.arange(n),nn];m=vsa[:,None]-vt;guard=1e-10*(1+abs(vsa[:,None])+abs(vt));m[np.arange(n),nn]=np.inf;guard[np.arange(n),nn]=0;passed=np.all(m>guard,axis=1)
                        rho=np.zeros((10,10));simple=np.zeros((10,10));ABt=At@Bt
                        for a in range(10):
                            for b in range(10):
                                if a==b:continue
                                l=Bs[:,a]-Bt[:,b];u=Bt[:,a]-Bs[:,b];zl=As@np.maximum(l,0)+At@np.minimum(l,0);zu=At@np.maximum(u,0)+As@np.minimum(u,0);rho[a,b]=np.linalg.norm(np.maximum(abs(zl),abs(zu)));simple[a,b]=np.linalg.norm(ABt[:,a]+ABt[:,b])
                        threshold=np.full(n,np.inf);simple_threshold=np.full(n,np.inf)
                        for q in np.flatnonzero(passed):
                            threshold[q]=(1+1e-10)*np.max(rn[q]*rho[nn[q]]/m[q])+1e-10
                            simple_threshold[q]=(1+1e-10)*np.max(rn[q]*simple[nn[q]]/m[q])+1e-10
                        assert np.all(threshold[passed]<=simple_threshold[passed]*(1+1e-12))
                        base=dict(dataset=dataset,seed=seed,K=100,n=n,t_over_sC=ratio,s_over_t=frac,sigma_s=float(s),sigma_t=float(t),At_operator_norm=op,At_trace=trace,positive_interval_margin_queries=int(passed.sum()),positive_interval_margin_pct=float(passed.mean()*100),minimum_positive_interval_margin=float(np.min(m[passed])) if passed.any() else None)
                        for method,th in [('signed_interval',threshold),('positive_sum',simple_threshold)]:
                            normth=th/op;valid=normth[passed];r=dict(base,method=method)
                            for quant in [0,.25,.5,.75,.9,1]:r['threshold_over_operator_q'+str(quant)]=float(np.quantile(valid,quant)) if len(valid) else None
                            for mult in p['normalized_penalty_thresholds']:r['certified_pct_at_'+str(mult)+'_times_operator']=float(np.mean(th<=mult*op)*100)
                            rec.append(r)
                        for key,arr in dict(threshold=threshold,simple_threshold=simple_threshold,positive_margin_mask=passed,margins=m,margin_guard=guard,rho=rho,simple_rho=simple,B_s=Bs,B_t=Bt,A_s=As,A_t=At).items():all_arrays[f'case{case}_{key}']=arr
                        case+=1
                np.savez_compressed(out/f'{name}.npz',nearest_prototype=nn,query_ids=qids,**all_arrays);timings.append(dict(group=name,seconds=time.perf_counter()-t0));print(json.dumps(timings[-1]),flush=True)
    csvwrite(out/'per_seed.csv',rec);summary=[]
    for d in ['mnist','fashion_mnist']:
        for ratio in [.5,1.]:
            for frac in [.99,.95]:
                for method in ['signed_interval','positive_sum']:
                    rr=[r for r in rec if r['dataset']==d and r['t_over_sC']==ratio and r['s_over_t']==frac and r['method']==method];row=dict(dataset=d,t_over_sC=ratio,s_over_t=frac,method=method,seeds=5)
                    for metric in ['positive_interval_margin_pct']+['certified_pct_at_'+str(v)+'_times_operator' for v in p['normalized_penalty_thresholds']]:
                        v=np.array([r[metric] for r in rr]);row[metric+'_mean']=float(v.mean());row[metric+'_sd_pp']=float(v.std(ddof=1))
                    for metric in ['threshold_over_operator_q0.5','threshold_over_operator_q0.9']:
                        v=[r[metric] for r in rr if r[metric] is not None];row['mean_seed_'+metric]=float(np.mean(v)) if v else None
                    summary.append(row)
    csvwrite(out/'summary.csv',summary);js(out/'COMPLETE.json',dict(runtime_seconds=time.perf_counter()-start,timings=timings,protocol_sha256=sha(HERE/'local_tail_protocol.json'),runner_sha256=sha(Path(__file__)),groups=10,local_bands=40,readout_fits=0,units='penalty lambda in original unnormalized sum-of-squares objective; normalized penalty lambda / spectral norm(H_t^T H_t)',strictness='margins guarded and thresholds inflated by 1+1e-10 plus 1e-10; no outward-rounded interval arithmetic'))
    js(out/'MANIFEST_SHA256.json',{q.name:sha(q) for q in out.iterdir() if q.is_file()})
if __name__=='__main__':main()
