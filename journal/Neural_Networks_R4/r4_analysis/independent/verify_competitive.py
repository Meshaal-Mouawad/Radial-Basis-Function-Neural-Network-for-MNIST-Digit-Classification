#!/usr/bin/env python3
"""Independently reconstruct R4 E/G from raw images and archived readout weights.

The sharp certificate is implemented directly from its equations. No production
certificate or R4 runner is imported. This verifier performs no model fitting.
"""
import csv,gzip,hashlib,json,time
from pathlib import Path
import numpy as np
from scipy.io import loadmat
from scipy.spatial.distance import cdist
from threadpoolctl import threadpool_limits

HERE=Path(__file__).resolve().parent; ROOT=HERE.parents[1]
BASE=ROOT/'evidence/baseline/evidence/baseline'; EXP=BASE/'work/v2/experiment/results'
OUT=ROOT/'r4_analysis/competitive/results'

def records(name):
    with (OUT/name).open() as f:return list(csv.DictReader(f))
def flat(x):return np.stack([a.ravel(order='F') for a in x]).astype(float)/255
def im(p):
    b=gzip.decompress(p.read_bytes());s=np.frombuffer(b[:16],'>u4');return np.frombuffer(b[16:],np.uint8).reshape(tuple(s[1:]))
def yi(p):return np.frombuffer(gzip.decompress(p.read_bytes())[8:],np.uint8).astype(int)
def check(value,saved,tol=1e-10):
    assert abs(float(value)-float(saved))<tol,(value,saved)
def oppose(scores,nn):
    own=scores[np.arange(len(nn)),nn]
    delta=scores-own[:,None];tol=1e-10*(1+abs(scores)+abs(own[:,None]));delta[np.arange(len(nn)),nn]=-np.inf
    return np.any(delta>tol,axis=1)
def jac(a,b):
    u=np.count_nonzero(a|b);return np.count_nonzero(a&b)/u if u else 1.

def main():
    started=time.perf_counter();totals=dict(groups=0,validation_labels=0,evaluation_labels=0,sharp_masks=0,original_mask_reproductions=0,surface_rows=0,competitive_rows=0,class_rows=0,budget_pairs=0,cross_seed_pairs=0)
    surface={(r['dataset'],int(r['seed']),int(r['K']),int(r['width_index']),int(r['penalty_index'])):r for r in records('surface_per_model.csv')}
    sets={(r['dataset'],int(r['seed']),int(r['K']),float(r['threshold'])):r for r in records('competitive_sets_per_seed.csv')}
    bestrows={(r['dataset'],int(r['seed']),int(r['K'])):r for r in records('validation_best_per_seed.csv')}
    classes={(r['dataset'],int(r['seed']),int(r['K']),int(r['class_label'])):r for r in records('validation_best_class_counts.csv')}
    groups={};max_mask_coverage_in_primary=0
    for ds in ['mnist','fashion_mnist']:
        if ds=='mnist':
            m=loadmat(BASE/'repository/Code/MNIST_train.mat');images=m['imagestrain'].transpose(2,0,1);labels=m['labelstrain'].ravel().astype(int);qi=np.load(BASE/'work/v2/design/reserved_training_ids.npy');qimages=images[qi];truth=labels[qi]
        else:
            p=BASE/'work/v2/data/fashion_mnist';images=im(p/'train-images-idx3-ubyte.gz');labels=yi(p/'train-labels-idx1-ubyte.gz');qimages=im(p/'t10k-images-idx3-ubyte.gz');truth=yi(p/'t10k-labels-idx1-ubyte.gz')
        Q=flat(qimages)
        for seed in [11,22,33,44,55]:
          for K in [50,100,200]:
            name=f'{ds}_seed{seed}_K{K}';old=np.load(EXP/name/'predictions_before_labels.npz');new=np.load(OUT/f'{name}.npz');widths=old['probe_widths'];penalties=old['probe_penalties'];n=len(truth)
            assert np.all(np.diff(widths)>0) and np.all(np.diff(penalties)>0)
            train=old['train_ids'];valid=old['validation_ids'];qid=old['query_ids'];assert not np.intersect1d(train,valid).size
            if ds=='mnist':assert not np.intersect1d(valid,qid).size
            C=flat(images[old['center_ids']]);DT=cdist(flat(images[train]),C,'sqeuclidean');DV=cdist(flat(images[valid]),C,'sqeuclidean');D=cdist(Q,C,'sqeuclidean');nn=old['center_labels'][D.argmin(1)];Yc=np.eye(10)[old['center_labels']];y=labels[train];non=np.ones(len(train),bool);non[old['center_rows']]=False
            assert np.array_equal(nn,new['nearest_prototype']) and np.array_equal(truth,new['truth'])
            nearest2=np.sort(D,axis=1)[:,:2];unique=nearest2[:,1]-nearest2[:,0]>1e-12*np.maximum(1,nearest2.max(1))
            validation=np.zeros((16,6),int);vp=np.empty((16,6,len(valid)),np.int8);pred=np.empty((16,6,n),np.int8);cert=np.zeros((16,6,n),bool);finite=cert.copy();limit=np.zeros((16,n),bool)
            for wi,w in enumerate(widths):
                rq=np.exp(-(D-D.min(1,keepdims=True))/(2*w*w));rv=np.exp(-(DV-DV.min(1,keepdims=True))/(2*w*w));H=np.exp(-DT/(2*w*w));H[old['center_rows'],np.arange(K)]=1
                Z=np.stack([H[y==c].sum(0) for c in range(10)],axis=1);limit[wi]=oppose(rq@Z,nn)
                E=H.copy();E[old['center_rows'],np.arange(K)]=0
                V=E[old['center_rows']]@Yc;P=np.stack([E[non&(y==c)].sum(0) for c in range(10)],axis=1);Qterm=E.T@(E@Yc);gamma=max(1-E[old['center_rows']].sum(1).max(),0)**2
                Vp=V[:,:,None]+V[:,None,:];Pp=P[:,:,None]+P[:,None,:];Qp=Qterm[:,:,None]+Qterm[:,None,:];rhs_tail=np.sqrt(np.sum((Vp+Pp)**2,axis=0));lhs=1-rq@Yc;norm=np.sqrt(np.sum(rq*rq,axis=1))
                for li,lam in enumerate(penalties):
                    W=old['weights'][wi,li];vp[wi,li]=(rv@W).argmax(1);validation[wi,li]=np.count_nonzero(vp[wi,li]==labels[valid]);score=rq@W;pred[wi,li]=score.argmax(1);finite[wi,li]=oppose(score,nn)
                    if lam==0 and old['numerical_ranks'][wi]<K:finite[wi,li]=False
                    if gamma+lam>0:
                        at=(abs(lam-1)*Vp+(lam+1)*Pp+Qp)/(gamma+lam);bound=np.maximum(np.sqrt(np.sum(at*at,axis=0)),rhs_tail);np.fill_diagonal(bound,0);rhs=norm[:,None]*bound[nn];passpair=(lhs-rhs)>1e-10*(1+abs(lhs)+abs(rhs));passpair[np.arange(n),nn]=True;cert[wi,li]=unique&passpair.all(1)
                    assert not np.any(cert[wi,li]&(pred[wi,li]!=nn))
                    oldwi=np.flatnonzero(np.isclose(old['width_upper_bounds'],w,rtol=1e-13,atol=0));oldli=np.flatnonzero(old['lambda_lower_bounds']==lam)
                    if len(oldwi) and len(oldli):
                        assert np.array_equal(cert[wi,li],old['certificate_masks'][oldwi[0],oldli[0],0]);totals['original_mask_reproductions']+=1
            assert np.array_equal(vp,new['validation_predictions']);assert np.array_equal(validation,new['validation_correct']);assert np.array_equal(pred,new['predictions']);assert np.array_equal(pred,old['predictions']);assert np.array_equal(cert,new['certificate']);assert np.array_equal(finite,new['finite_endpoint']);assert np.array_equal(limit,new['limit_endpoint'])
            best=max((int(validation[i,j]),-float(widths[i]),-int(penalties[j]),i,j) for i in range(16) for j in range(6));bi,bj=best[-2:];assert bi==int(new['best_width_index']) and bj==int(new['best_penalty_index'])
            comp=np.stack([validation>=q*validation.max() for q in [.9,.95,.99]]);assert np.array_equal(comp,new['competitive'])
            prefix=np.logical_or.accumulate(limit,axis=0);fregion=np.zeros_like(finite)
            for wi,w in enumerate(widths):
                for li,lam in enumerate(penalties):
                    fregion[wi,li]=np.any(finite[(widths<=w)][:,penalties>=lam],axis=(0,1))
            excluded=fregion|prefix[:,None,:];assert np.array_equal(prefix,new['limit_prefix']);assert np.array_equal(fregion,new['finite_region']);assert np.array_equal(excluded,new['excluded_region']);assert not np.any(cert&excluded)
            for wi in range(16):
                for li in range(6):
                    rr=surface[(ds,seed,K,wi,li)];correct=pred[wi,li]==truth;agreement=pred[wi,li]==nn
                    for key,val in dict(validation_correct=validation[wi,li],validation_accuracy_pct=validation[wi,li]/len(valid)*100,evaluation_accuracy_pct=correct.mean()*100,nearest_accuracy_pct=(nn==truth).mean()*100,nearest_agreement_pct=agreement.mean()*100,certified=cert[wi,li].sum(),certificate_coverage_pct=cert[wi,li].mean()*100,limit_prefix_exclusion_pct=prefix[wi].mean()*100,finite_region_exclusion_pct=fregion[wi,li].mean()*100,combined_region_exclusion_pct=excluded[wi,li].mean()*100,unresolved_region_pct=(~excluded[wi,li]&~cert[wi,li]).mean()*100).items():check(val,rr[key])
                    if cert[wi,li].any():check(correct[cert[wi,li]].mean()*100,rr['certified_accuracy_pct'])
                    else:assert rr['certified_accuracy_pct']==''
                    assert (rr['validation_best']=='True')==(wi==bi and li==bj)
                    totals['surface_rows']+=1
            for j,q in enumerate([.9,.95,.99]):
                rr=sets[(ds,seed,K,q)];mask=comp[j];check(mask.sum(),rr['retained_models']);check(cert[mask].sum(),rr['certified_query_model_count']);assert (rr['all_retained_zero_coverage']=='True')==(not cert[mask].any());check(cert[mask].any(0).sum(),rr['any_retained_certified_queries']);totals['competitive_rows']+=1
                if q==.95:max_mask_coverage_in_primary=max(max_mask_coverage_in_primary,int(cert[mask].sum()))
            bp=pred[bi,bj];br=bestrows[(ds,seed,K)];check(bi,br['width_index']);check(bj,br['penalty_index'])
            for c in range(10):
                rr=classes[(ds,seed,K,c)];true=truth==c;pc=bp==c
                for key,val in dict(evaluation_class_count=true.sum(),predicted_count=pc.sum(),correct_count=(true&pc).sum(),certified_class_count=(true&cert[bi,bj]).sum(),recall_pct=(true&pc).sum()/true.sum()*100,prediction_share_pct=pc.mean()*100).items():check(val,rr[key])
                totals['class_rows']+=1
            groups[(ds,seed,K)]=dict(pred=bp,correct=bp==truth,cert=cert[bi,bj],qid=qid,valid=valid,truth=truth,nn=nn,val_acc=validation[bi,bj]/len(valid)*100,eval_acc=(bp==truth).mean()*100,agree=(bp==nn).mean()*100)
            totals['groups']+=1;totals['validation_labels']+=vp.size;totals['evaluation_labels']+=pred.size;totals['sharp_masks']+=96;print(name,'PASS',flush=True)
    for rr in records('budget_paired_per_seed.csv'):
        ds=rr['dataset'];seed=int(rr['seed']);ka=int(rr['K_low']);kb=int(rr['K_high']);a=groups[(ds,seed,ka)];b=groups[(ds,seed,kb)];assert np.array_equal(a['qid'],b['qid'])
        for key,val in dict(evaluation_accuracy_difference_pp=b['eval_acc']-a['eval_acc'],validation_accuracy_difference_pp=b['val_acc']-a['val_acc'],nearest_agreement_difference_pp=b['agree']-a['agree'],prediction_disagreement_pct=(a['pred']!=b['pred']).mean()*100,correctness_jaccard=jac(a['correct'],b['correct']),certificate_jaccard=jac(a['cert'],b['cert']),correct_high_only=(b['correct']&~a['correct']).sum(),correct_low_only=(a['correct']&~b['correct']).sum()).items():check(val,rr[key])
        totals['budget_pairs']+=1
    for rr in records('cross_seed_stability.csv'):
        ds=rr['dataset'];K=int(rr['K']);a=groups[(ds,int(rr['seed1']),K)];b=groups[(ds,int(rr['seed2']),K)];assert np.array_equal(a['qid'],b['qid'])
        for key,val in dict(shared_evaluation_queries=len(a['qid']),prediction_disagreement_pct=(a['pred']!=b['pred']).mean()*100,correctness_jaccard=jac(a['correct'],b['correct']),certificate_jaccard=jac(a['cert'],b['cert']),correct_both=(a['correct']&b['correct']).sum(),validation_id_overlap=len(np.intersect1d(a['valid'],b['valid']))).items():check(val,rr[key])
        totals['cross_seed_pairs']+=1
    report=dict(status='PASS',method='Raw-image reconstruction, independently coded sharp inequality and fixed validation selection; no production-runner imports',counts=totals,maximum_primary_group_certified_query_model_count=max_mask_coverage_in_primary,all_original_630_masks_match=True,all_stability_query_masks_match=True,new_fits=0,elapsed_seconds=time.perf_counter()-started,script_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest())
    (HERE/'competitive_verification.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))

if __name__=='__main__':
    with threadpool_limits(1):main()
