#!/usr/bin/env python3
"""Post hoc diagnostic; immutable archived observations, no model refitting."""
import argparse,csv,gzip,hashlib,json,struct,time,sys,platform
from pathlib import Path
from datetime import datetime,timezone
import numpy as np
from scipy.io import loadmat
from scipy.spatial.distance import cdist
from threadpoolctl import threadpool_limits
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
BASE=ROOT/'baseline/evidence/baseline'
EXP=BASE/'work/v2/experiment/results'
FRONT=ROOT/'baseline/evidence/frontier/results'
def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def js(p,v):p.write_text(json.dumps(v,indent=2,allow_nan=False)+'\n')
def csvwrite(p,rows):
    with p.open('w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
def idx(p):
    b=gzip.decompress(p.read_bytes());magic,n,r,c=struct.unpack('>IIII',b[:16]);assert magic==2051
    return np.frombuffer(b,np.uint8,offset=16).reshape(n,r,c)
def flatten(a):return a.transpose(0,2,1).reshape(len(a),-1).astype(float)/255

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--dense',action='store_true');ap.add_argument('--guarded-finite',action='store_true');a=ap.parse_args()
    stage=('dense67' if a.dense else 'original7')+('_guarded' if a.guarded_finite else '');out=HERE/stage;out.mkdir(exist_ok=False)
    expected=(HERE/'PROTOCOL_SHA256.txt').read_text().split()[0];assert sha(HERE/'protocol.json')==expected
    start=time.perf_counter();records=[];times=[];inputs={};original_crosscheck=0.
    with threadpool_limits(1):
        for dataset in ['mnist','fashion_mnist']:
            if dataset=='mnist':
                d=loadmat(BASE/'repository/Code/MNIST_train.mat');images=d['imagestrain'].transpose(2,0,1);labels=d['labelstrain'].ravel().astype(int)
                qimages=images[np.load(BASE/'work/v2/design/reserved_training_ids.npy')]
            else:
                folder=BASE/'work/v2/data/fashion_mnist';images=idx(folder/'train-images-idx3-ubyte.gz');qimages=idx(folder/'t10k-images-idx3-ubyte.gz')
                b=gzip.decompress((folder/'train-labels-idx1-ubyte.gz').read_bytes());labels=np.frombuffer(b,np.uint8,offset=8).astype(int)
            Xq=flatten(qimages);truth=np.load(EXP/f'{dataset}_evaluation_labels.npy')
            for seed in [11,22,33,44,55]:
                t0=time.perf_counter();name=f'{dataset}_seed{seed}_K100';orig=EXP/name/'predictions_before_labels.npz';inputs[str(orig.relative_to(ROOT))]=sha(orig)
                with np.load(orig) as z:
                    train_ids=z['train_ids'];rows=z['center_rows'];center_ids=z['center_ids'];yc=z['center_labels'];nn=z['nearest_prototype'];query_ids=z['query_ids'];oldwidth=z['width_upper_bounds'];scale=float(oldwidth[1]*16)
                    oldB=np.eye(10)[yc][None,:,:]+z['V']+z['P'];oldpred=z['predictions'];probe_width=z['probe_widths'];probe_penalty=z['probe_penalties'];floors=z['lambda_lower_bounds'];oldmask=z['certificate_masks'][:,:,0];oldweights=z['weights'];ranks=z['numerical_ranks']
                assert np.array_equal(center_ids,train_ids[rows]);C=flatten(images[center_ids]);Dq=cdist(Xq,C,'sqeuclidean');Dq-=Dq.min(axis=1,keepdims=True);n=len(nn)
                assert n==len(truth) and np.array_equal(yc[np.argmin(Dq,axis=1)],nn)
                if a.dense:
                    archive=FRONT/name/'frontiers_before_labels.npz';inputs[str(archive.relative_to(ROOT))]=sha(archive)
                    with np.load(archive) as z:width=z['widths'];ratios=z['ratios'];mask=z['certificate_masks'][:,:,0];assert np.array_equal(nn,z['nearest_prototype'])
                    X=flatten(images[train_ids]);Y=np.eye(10)[labels[train_ids]];Dt=cdist(X,C,'sqeuclidean')
                else:width=oldwidth;ratios=width/scale;mask=oldmask
                finite_source=oldpred!=nn
                if a.guarded_finite:
                    finite_source=np.zeros_like(oldpred,dtype=bool)
                    for pi,pw in enumerate(probe_width):
                        rq=np.exp(-Dq/(2*pw*pw))
                        for lj,penalty in enumerate(probe_penalty):
                            if penalty==0 and ranks[pi]<100:continue
                            sc=rq@oldweights[pi,lj];ns=sc[np.arange(n),nn];sc[np.arange(n),nn]=-np.inf;cs=sc.max(axis=1)
                            finite_source[pi,lj]=cs-ns>1e-10*(1+abs(cs)+abs(ns))
                nw=len(width);Bsave=np.zeros((nw,100,10));obstruct=np.zeros((nw,n),bool);delta=np.zeros((nw,n));guard=np.zeros((nw,n));near_score=np.zeros((nw,n));competitor_score=np.zeros((nw,n));pred=np.zeros((nw,n),np.int8)
                for wi,t in enumerate(width):
                    if a.dense:
                        H=np.exp(-Dt/(2*t*t));H[rows,np.arange(100)]=1;B=H.T@Y
                        oldmatch=np.flatnonzero(np.isclose(oldwidth,t,rtol=1e-13,atol=0))
                        for oi in oldmatch:original_crosscheck=max(original_crosscheck,float(np.max(np.abs(B-oldB[oi]))))
                    else:B=oldB[wi]
                    Bsave[wi]=B;r=np.exp(-Dq/(2*t*t));scores=r@B;pred[wi]=scores.argmax(axis=1);ns=scores[np.arange(n),nn];scores[np.arange(n),nn]=-np.inf;cs=scores.max(axis=1)
                    g=1e-10*(1+np.abs(ns)+np.abs(cs));dd=cs-ns;obstruct[wi]=dd>g;delta[wi]=dd;guard[wi]=g;near_score[wi]=ns;competitor_score[wi]=cs
                prefix=np.zeros_like(obstruct);finite=np.zeros((nw,3,n),bool)
                for wi,t in enumerate(width):
                    relevant=np.flatnonzero(width<=t*(1+1e-14));prefix[wi]=np.any(obstruct[relevant],axis=0)
                    pi=np.flatnonzero(probe_width<=t*(1+1e-14))
                    for li,lo in enumerate(floors):
                        lj=np.flatnonzero(probe_penalty>=lo)
                        if len(pi):finite[wi,li]=np.any(finite_source[pi[:,None],lj[None,:]],axis=(0,1))
                        cm=mask[wi,li];ex=prefix[wi]|finite[wi,li];assert not np.any(cm&ex),(name,wi,lo)
                        records.append(dict(dataset=dataset,seed=seed,K=100,width_index=wi,sigma=float(t),sigma_over_sC=float(ratios[wi]),lambda_floor=int(lo),n=n,certified=int(cm.sum()),limit_endpoint_excluded=int(obstruct[wi].sum()),limit_prefix_excluded=int(prefix[wi].sum()),finite_probe_excluded=int(finite[wi,li].sum()),combined_excluded=int(ex.sum()),unresolved=int((~cm&~ex).sum()),limit_argmax_agreement=int((pred[wi]==nn).sum()),limit_true_correct=int((pred[wi]==truth).sum()),nearest_true_correct=int((nn==truth).sum())))
                np.savez_compressed(out/f'{name}.npz',widths=width,ratios=ratios,floors=floors,train_ids=train_ids,center_ids=center_ids,center_rows=rows,center_labels=yc,query_ids=query_ids,nearest_prototype=nn,HtY=Bsave,limit_argmax=pred,limit_competing_minus_nearest=delta,sign_guard=guard,nearest_limit_score=near_score,best_competing_limit_score=competitor_score,endpoint_obstruction=obstruct,prefix_obstruction=prefix,finite_probe_obstruction=finite,sharp_certificate_masks=mask)
                times.append(dict(group=name,seconds=time.perf_counter()-t0));print(json.dumps(times[-1]),flush=True)
    csvwrite(out/'rectangles.csv',records);summary=[]
    for dataset in ['mnist','fashion_mnist']:
        for wi in range(nw):
            for lo in floors:
                rr=[r for r in records if r['dataset']==dataset and r['width_index']==wi and r['lambda_floor']==lo];row=dict(dataset=dataset,width_index=wi,sigma_over_sC_mean=float(np.mean([r['sigma_over_sC'] for r in rr])),lambda_floor=int(lo),seeds=5,n_per_seed=rr[0]['n'])
                for metric in ['certified','limit_endpoint_excluded','limit_prefix_excluded','finite_probe_excluded','combined_excluded','unresolved','limit_argmax_agreement','limit_true_correct','nearest_true_correct']:
                    v=np.array([r[metric]/r['n']*100 for r in rr]);row[metric+'_mean_pct']=float(v.mean());row[metric+'_sd_pp']=float(v.std(ddof=1))
                summary.append(row)
    csvwrite(out/'summary.csv',summary)
    js(out/'COMPLETE.json',dict(stage=stage,completed_utc=datetime.now(timezone.utc).isoformat(),runtime_seconds=time.perf_counter()-start,group_timing=times,groups=10,rectangles=len(records),query_width_cases=sum(r['n'] for r in records)//3,protocol_sha256=expected,runner_sha256=sha(Path(__file__)),input_sha256=inputs,maximum_original_HtY_crosscheck_absolute_error=original_crosscheck,finite_score_guarded=a.guarded_finite,python=sys.version,numpy=np.__version__,platform=platform.platform(),certified_excluded_intersection=0))
    js(out/'MANIFEST_SHA256.json',{p.name:sha(p) for p in sorted(out.iterdir()) if p.is_file()})
if __name__=='__main__':main()
