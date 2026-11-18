#!/usr/bin/env python3
"""Reconstruct archived RBF scores and evaluate label-free equal-size selectors."""
import argparse,csv,gzip,hashlib,json,platform,struct,time
from pathlib import Path
import numpy as np
from scipy.io import loadmat
from scipy.spatial.distance import cdist
from threadpoolctl import threadpool_limits

HERE=Path(__file__).resolve().parent
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def js(p,x):p.write_text(json.dumps(x,indent=2,allow_nan=False)+'\n')
def csvwrite(p,rows):
    with p.open('w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
def idx(p):
    b=gzip.decompress(p.read_bytes());magic,n,r,c=struct.unpack('>IIII',b[:16]);assert magic==2051
    return np.frombuffer(b,np.uint8,offset=16).reshape(n,r,c)
def flatten(a):return a.transpose(0,2,1).reshape(len(a),-1).astype(float)/255.
def top_mask(scores,m,query_ids,eligible=None):
    ids=np.arange(len(scores)) if eligible is None else np.flatnonzero(eligible)
    assert len(ids)>=m
    ix=ids[np.lexsort((ids,query_ids[ids],-scores[ids]))[:m]]
    mask=np.zeros(len(scores),bool);mask[ix]=True
    assert mask.sum()==m
    return mask

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--evidence',type=Path,default=HERE.parents[1]/'evidence');ap.add_argument('--output',type=Path,default=HERE/'results');a=ap.parse_args()
    root=a.evidence.resolve();out=a.output.resolve();out.mkdir(parents=True,exist_ok=True)
    base=root/'baseline/evidence/baseline';exp=base/'work/v2/experiment/results';diag=root/'new_analysis/limit_diagnostic'
    start=time.perf_counter();rows=[];distrows=[];labelrows=[];input_hashes={};reconstructed=0;max_score_scale_error=0.
    def record(p):input_hashes[str(p.relative_to(root))]=sha(p)
    with threadpool_limits(1):
        for d in ['mnist','fashion_mnist']:
            if d=='mnist':
                f=base/'repository/Code/MNIST_train.mat';record(f);z=loadmat(f);images=z['imagestrain'].transpose(2,0,1);train_labels=z['labelstrain'].ravel().astype(int)
                f=base/'work/v2/design/reserved_training_ids.npy';record(f);qimages=images[np.load(f)]
            else:
                f=base/'work/v2/data/fashion_mnist';images=idx(f/'train-images-idx3-ubyte.gz');qimages=idx(f/'t10k-images-idx3-ubyte.gz');train_labels=np.frombuffer(gzip.decompress((f/'train-labels-idx1-ubyte.gz').read_bytes()),np.uint8,offset=8).astype(int)
                for n in ['train-images-idx3-ubyte.gz','t10k-images-idx3-ubyte.gz','train-labels-idx1-ubyte.gz']:record(f/n)
            Xq=flatten(qimages);f=exp/f'{d}_evaluation_labels.npy';record(f);truth=np.load(f);n=len(truth)
            truecounts=np.bincount(truth,minlength=10);query_majority=int(truecounts.argmax())
            for k in range(10):labelrows.append(dict(dataset=d,class_label=k,n=n,count=int(truecounts[k]),share_pct=float(truecounts[k]/n*100)))
            for seed in [11,22,33,44,55]:
                name=f'{d}_seed{seed}_K100';orig=exp/name/'predictions_before_labels.npz';local=diag/'local_tail'/f'{name}.npz';validation=diag/'local_tail_validation'/f'{name}.npz'
                for p in [orig,local,validation]:record(p)
                with np.load(orig) as z:
                    C=flatten(images[z['center_ids']]);yc=z['center_labels'];nn=z['nearest_prototype'];scale=float(z['width_upper_bounds'][1]*16);qid=z['query_ids'];train_ids=z['train_ids']
                train_majority=int(np.bincount(train_labels[train_ids],minlength=10).argmax())
                D=cdist(Xq,C,'sqeuclidean');dmin=D.min(axis=1);Dshift=D-dmin[:,None]
                assert np.array_equal(nn,yc[D.argmin(axis=1)])
                otherD=np.where(yc[None,:]!=nn[:,None],D,np.inf)
                distance_margin=otherD.min(axis=1)-dmin
                assert np.all(np.isfinite(distance_margin))
                saved={'truth':truth,'nearest_prototype':nn,'query_ids':qid,'prototype_distance_margin':distance_margin}
                with np.load(local) as z,np.load(validation) as v:
                    for ri,ratio in enumerate([.5,1.]):
                        ci=2*ri;t=ratio*scale;op=float(np.linalg.eigvalsh(z[f'case{ci}_A_t'])[-1]);W=v[f't{ri}_weights'][0,2];pred=v[f't{ri}_predictions'][0,2]
                        scores=np.exp(-D/(2*t*t))@W
                        normalized=np.exp(-Dshift/(2*t*t))@W
                        assert np.array_equal(pred,scores.argmax(axis=1)) and np.array_equal(pred,normalized.argmax(axis=1))
                        reconstructed+=n
                        max_score_scale_error=max(max_score_scale_error,float(np.max(np.abs(scores-normalized*np.exp(-dmin/(2*t*t))[:,None]))))
                        sorted_scores=np.sort(scores,axis=1);margin=sorted_scores[:,-1]-sorted_scores[:,-2]
                        sorted_norm=np.sort(normalized,axis=1);norm_margin=sorted_norm[:,-1]-sorted_norm[:,-2]
                        cert=z[f'case{ci}_threshold']<=10*op;m=int(cert.sum());assert m>0 and np.all(pred[cert]==nn[cert])
                        agreement=pred==nn;correct=pred==truth
                        masks={'certificate':cert,
                               'score_margin':top_mask(margin,m,qid),
                               'normalized_score_margin':top_mask(norm_margin,m,qid),
                               'prototype_distance_margin':top_mask(distance_margin,m,qid),
                               'agreement_gated_score_margin':top_mask(margin,m,qid,agreement),
                               'agreement_gated_distance_margin':top_mask(distance_margin,m,qid,agreement)}
                        certacc=float(correct[cert].mean()*100)
                        for selector,mask in {'full_query':np.ones(n,bool),**masks}.items():
                            nc=int(mask.sum());acc=float(correct[mask].mean()*100);pc=np.bincount(pred[mask],minlength=10);tc=np.bincount(truth[mask],minlength=10);pr=pc/nc;entropy=float(-np.sum(pr[pr>0]*np.log2(pr[pr>0])))
                            rows.append(dict(dataset=d,seed=seed,t_over_sC=ratio,s_over_t=.99,lambda_over_At_operator=10,selector=selector,n=n,selected=nc,coverage_pct=nc/n*100,correct=int(correct[mask].sum()),accuracy_pct=acc,certificate_minus_selector_pp=certacc-acc,nearest_agreement_pct=float(agreement[mask].mean()*100),dominant_prediction=int(pc.argmax()),dominant_prediction_pct=float(pc.max()/nc*100),prediction_entropy_bits=entropy,query_majority_label=query_majority,query_majority_reference_pct=float(truecounts.max()/n*100),training_majority_label=train_majority,training_majority_accuracy_pct=float(np.mean(truth==train_majority)*100),certificate_overlap=int((cert&mask).sum()),agreement_pool_size=int(agreement.sum())))
                            for k in range(10):distrows.append(dict(dataset=d,seed=seed,t_over_sC=ratio,selector=selector,class_label=k,selected=nc,predicted_count=int(pc[k]),true_count=int(tc[k])))
                        saved[f't{ri}_predictions']=pred;saved[f't{ri}_raw_scores']=scores;saved[f't{ri}_normalized_scores']=normalized;saved[f't{ri}_score_margin']=margin;saved[f't{ri}_normalized_margin']=norm_margin
                        for k,mask in masks.items():saved[f't{ri}_{k}_mask']=mask
                np.savez_compressed(out/f'{name}.npz',**saved)
    csvwrite(out/'per_seed.csv',rows);csvwrite(out/'class_counts.csv',distrows);csvwrite(out/'query_label_distribution.csv',labelrows)
    summary=[]
    for d in ['mnist','fashion_mnist']:
        for ratio in [.5,1.]:
            for selector in ['full_query','certificate','score_margin','normalized_score_margin','prototype_distance_margin','agreement_gated_score_margin','agreement_gated_distance_margin']:
                rr=[r for r in rows if r['dataset']==d and r['t_over_sC']==ratio and r['selector']==selector];assert len(rr)==5
                s=dict(dataset=d,t_over_sC=ratio,selector=selector,seeds=5,n_per_seed=rr[0]['n'])
                for field in ['selected','coverage_pct','accuracy_pct','certificate_minus_selector_pp','nearest_agreement_pct','dominant_prediction_pct','prediction_entropy_bits']:
                    values=np.array([r[field] for r in rr]);s[field+'_mean']=float(values.mean());s[field+'_sd']=float(values.std(ddof=1))
                summary.append(s)
    csvwrite(out/'summary.csv',summary)
    js(out/'verification.json',dict(status='PASS',new_model_fits=0,reconstructed_endpoint_prediction_labels=reconstructed,maximum_raw_score_scaling_error=max_score_scale_error,certificate_disagreements=0,equal_cardinality_all_selectors=True,deterministic_label_free_selection=True,groups=10,settings_per_group=2,runtime_seconds=time.perf_counter()-start,numpy=np.__version__,platform=platform.platform(),protocol_sha256=sha(HERE/'protocol.json'),script_sha256=sha(Path(__file__)),inputs_sha256=input_hashes))
    js(out/'MANIFEST_SHA256.json',{p.name:sha(p) for p in sorted(out.iterdir()) if p.is_file() and p.name!='MANIFEST_SHA256.json'})
    print(json.dumps({'status':'PASS','labels':reconstructed,'runtime_seconds':time.perf_counter()-start,'output':str(out)}))
if __name__=='__main__':main()
