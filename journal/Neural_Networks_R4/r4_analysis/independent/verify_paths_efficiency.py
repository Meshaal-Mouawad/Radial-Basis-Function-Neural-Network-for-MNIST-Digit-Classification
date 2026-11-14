#!/usr/bin/env python3
"""Independent D/F replay from R2 image arrays and fitted weights.

Reconstructs all original margins/states and all finite witness masks, then
rebuilds prescribed probe order and every cumulative count. No new fitting.
"""
from pathlib import Path
import csv,gzip,hashlib,json,time
import numpy as np
from scipy.io import loadmat
from scipy.spatial.distance import cdist
from threadpoolctl import threadpool_limits

HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[1]
BASE=ROOT/'evidence/baseline/evidence/baseline';EXP=BASE/'work/v2/experiment/results';FRONT=ROOT/'evidence/baseline/evidence/frontier/results';DIAG=ROOT/'evidence/new_analysis/limit_diagnostic';R3=ROOT/'r3_analysis/m1_m2/results';OUT=ROOT/'r4_analysis/disagreement/results'
def rows(p):
    with p.open() as f:return list(csv.DictReader(f))
def flat(x):return np.stack([v.ravel(order='F') for v in x]).astype(float)/255
def img(p):
    b=gzip.decompress(p.read_bytes());sh=np.frombuffer(b[:16],'>u4');return np.frombuffer(b[16:],np.uint8).reshape(tuple(sh[1:]))
def scorestate(features,weights,nn):
    scores=features@weights;own=scores[np.arange(len(nn)),nn];other=scores.copy();other[np.arange(len(nn)),nn]=-np.inf;best=other.max(1);delta=best-own;guard=1e-10*(1+abs(best)+abs(own));state=np.where(delta>guard,1,np.where(delta<-guard,-1,0)).astype(np.int8)
    return delta,guard,state,scores.argmax(1)
def check(x,y):assert abs(float(x)-float(y))<1e-10,(x,y)
def order_for(meta,t,floor):
    # Width bins are constructed first, then penalty/source ordering within bins.
    ii=[i for i,x in enumerate(meta) if x['width']<=t*(1+1e-14) and x['penalty']>=floor]
    bins=[]
    for i in sorted(ii,key=lambda i:meta[i]['width']):
        if not bins or not np.isclose(meta[i]['width'],meta[bins[-1][0]]['width'],rtol=1e-13,atol=0):bins.append([])
        bins[-1].append(i)
    priority={'original':0,'frontier':1,'local_tail':2}
    bins=[sorted(b,key=lambda i:(meta[i]['penalty'],priority[meta[i]['source']],i)) for b in bins]
    result=[]
    for k in range(max(map(len,bins),default=0)):
        result.extend(b[k] for b in bins if len(b)>k)
    return result

def main():
    start=time.perf_counter();counts=dict(groups=0,prediction_labels=0,path_query_widths=0,path_summary_rows=0,bound_comparison_rows=0,finite_probe_masks=0,cumulative_probe_rows=0,efficiency_regions=0);allD=[];allF=[]
    for ds in ['mnist','fashion_mnist']:
        if ds=='mnist':
            x=loadmat(BASE/'repository/Code/MNIST_train.mat',variable_names=['imagestrain'])['imagestrain'].transpose(2,0,1);q=x[np.load(BASE/'work/v2/design/reserved_training_ids.npy')]
        else:
            p=BASE/'work/v2/data/fashion_mnist';x=img(p/'train-images-idx3-ubyte.gz');q=img(p/'t10k-images-idx3-ubyte.gz')
        Q=flat(q)
        for seed in [11,22,33,44,55]:
          for K in [50,100,200]:
            name=f'{ds}_seed{seed}_K{K}';old=np.load(EXP/name/'predictions_before_labels.npz');saved=np.load(OUT/f'{name}_paths.npz');D=cdist(Q,flat(x[old['center_ids']]),'sqeuclidean');D-=D.min(1,keepdims=True);nn=old['nearest_prototype'];pw=old['probe_widths'];pl=old['probe_penalties'];n=len(nn);states=np.empty((16,6,n),np.int8);margins=np.empty((16,6,n));guards=np.empty_like(margins);metadata=[];finite=[]
            for wi,w in enumerate(pw):
                features=np.exp(-D/(2*w*w))
                for li,lam in enumerate(pl):
                    d,g,st,pred=scorestate(features,old['weights'][wi,li],nn)
                    assert np.array_equal(pred,old['predictions'][wi,li])
                    if lam==0 and old['numerical_ranks'][wi]<K:st[:]=2
                    states[wi,li]=st;margins[wi,li]=d;guards[wi,li]=g;finite.append(st==1);metadata.append(dict(width=float(w),penalty=float(lam),source='original',source_width_index=wi,source_penalty_index=li));counts['prediction_labels']+=n
            assert np.array_equal(states,saved['state']);assert np.allclose(margins,saved['margin'],rtol=1e-13,atol=1e-14);assert np.allclose(guards,saved['guard'],rtol=1e-13,atol=1e-18)
            detected=(states==1).any(1);first=np.where(detected,(states==1).argmax(1),-1);indices=np.arange(6)[None,:,None];prev=np.max(np.where((states==-1)&(indices<np.where(detected,first,6)[:,None,:]),indices,-1),axis=1);lower=np.where(first>0,pl[np.maximum(first-1,0)],np.nan);upper=np.where(first>=0,pl[np.maximum(first,0)],np.nan)
            changes=np.zeros((16,n),np.int8);returns=np.zeros_like(changes);previous=np.zeros_like(changes)
            for j in range(6):
                current=states[:,j];valid=abs(current)==1;changes+=(valid&(previous!=0)&(current!=previous));returns+=(valid&(previous==1)&(current==-1));previous=np.where(valid,current,previous)
            for key,a in [('first_disagreement_index',first),('last_strict_agreement_before_first',prev),('sampled_sign_change_count',changes),('sampled_return_to_agreement_count',returns),('strict_agreement_all_samples',np.all(states==-1,axis=1)),('any_guard_sample',np.any(states==0,axis=1)),('any_invalid_sample',np.any(states==2,axis=1))]:assert np.array_equal(a,saved[key]),(name,key)
            assert np.array_equal(lower,saved['first_detection_lower_sample'],equal_nan=True);assert np.array_equal(upper,saved['first_detection_upper_sample'],equal_nan=True)
            csvrows=rows(OUT/f'{name}_D_per_width.csv');r3=np.load(R3/f'{name}.npz') if K==100 else None
            bmap=np.full(16,-1,int)
            if r3 is not None:
                for wi,w in enumerate(pw):
                    match=np.flatnonzero(np.isclose(r3['widths'],w,rtol=1e-13,atol=0))
                    if len(match):bmap[wi]=match[0]
                assert np.array_equal(saved['bound_raw'],r3['threshold']);assert np.array_equal(saved['bound_operator_norm'],r3['operator_norm'])
            assert np.array_equal(bmap,saved['bound_reference_index'])
            for wi in range(16):
                rr=csvrows[wi];firsti=first[wi];has=detected[wi];after=firsti>0;adj=np.zeros(n,bool);ix=np.flatnonzero(after);adj[ix]=states[wi,firsti[ix]-1,ix]==-1
                vals=dict(strict_disagreement_any=has.sum(),left_censored_first_disagreement=(firsti==0).sum(),first_detected_after_zero=after.sum(),adjacent_strict_agreement_disagreement_bracket=adj.sum(),first_detection_guard_or_invalid_lower=(after&~adj).sum(),no_disagreement_observed=(~has).sum(),strict_agreement_all_samples=np.all(states[wi]==-1,axis=0).sum(),no_disagreement_with_guard_samples=((~has)&np.any(states[wi]==0,axis=0)).sum(),any_guard_sample=np.any(states[wi]==0,axis=0).sum(),any_invalid_sample=np.any(states[wi]==2,axis=0).sum(),sampled_return_to_agreement=(returns[wi]>0).sum(),sampled_sign_changes_total=changes[wi].sum(),maximum_sampled_sign_changes=changes[wi].max(),bound_reference_index=bmap[wi])
                for k,v in vals.items():check(v,rr[k])
                allD.append(dict(dataset=ds,seed=seed,K=K,n=n,width_index=wi,**vals));counts['path_summary_rows']+=1
            counts['path_query_widths']+=16*n
            if K==100:
                for rr in rows(OUT/f'{name}_D_bounds.csv'):
                    wi=int(rr['probe_width_index']);bi=bmap[wi];B=r3['threshold'][bi];fb=np.isfinite(B);has=detected[wi];fp=upper[wi];rp=has&fb&(fp>0);rat=B[rp]/fp[rp];above=(pl[:,None]>B[None,:]*(1+1e-10))&fb[None,:]
                    vals=dict(finite_bound_queries=fb.sum(),no_finite_bound_queries=(~fb).sum(),observed_disagreement_with_finite_bound=(has&fb).sum(),observed_disagreement_without_finite_bound=(has&~fb).sum(),finite_bound_without_observed_disagreement=(fb&~has).sum(),first_observed_disagreement_below_bound=(has&fb&(fp<B)).sum(),finite_bound_above_largest_sampled_penalty=(fb&(B>pl[-1])).sum(),positive_first_penalty_ratio_cases=rp.sum(),grid_pairs_above_bound=above.sum(),above_bound_raw_margin_failures=(above&(margins[wi]<=0)).sum(),above_bound_not_guarded_disagreement=(above&(states[wi]!=1)).sum())
                    for k,v in vals.items():check(v,rr[k])
                    if len(rat):check(np.median(rat),rr['bound_over_first_positive_penalty_median']);check(np.quantile(rat,.9),rr['bound_over_first_positive_penalty_q90'])
                    else:assert rr['bound_over_first_positive_penalty_median']=='' and rr['bound_over_first_positive_penalty_q90']==''
                    counts['bound_comparison_rows']+=1
                front=np.load(FRONT/name/'frontiers_before_labels.npz')
                for wi,w in enumerate(front['widths'][front['fit_grid_indices']]):
                    features=np.exp(-D/(2*w*w))
                    for li,lam in enumerate(front['lambda_floors']):
                        _,_,st,pred=scorestate(features,front['weights'][wi,li],nn);assert np.array_equal(pred,front['predictions'][wi,li])
                        if lam==0 and front['numerical_ranks'][wi]<K:st[:]=2
                        finite.append(st==1);metadata.append(dict(width=float(w),penalty=float(lam),source='frontier',source_width_index=wi,source_penalty_index=li))
                fit=np.load(DIAG/'local_tail_validation'/f'{name}.npz');tail=np.load(DIAG/'local_tail'/f'{name}.npz');scale=old['width_upper_bounds'][1]*16
                for ri,ratio in enumerate([.5,1.]):
                    op=np.linalg.eigvalsh(tail[f'case{2*ri}_A_t'])[-1]
                    for li,mult in enumerate([10,100]):
                        for si,frac in enumerate([.95,.99,1.]):
                            w=scale*ratio*frac;_,_,st,pred=scorestate(np.exp(-D/(2*w*w)),fit[f't{ri}_weights'][li,si],nn);assert np.array_equal(pred,fit[f't{ri}_predictions'][li,si]);finite.append(st==1);metadata.append(dict(width=float(w),penalty=float(mult*op),source='local_tail',source_width_index=ri*3+si,source_penalty_index=li))
                finite=np.array(finite);savedfinite=np.load(OUT/f'{name}_finite_masks.npz');assert np.array_equal(finite,savedfinite['masks']);assert metadata==json.loads((OUT/f'{name}_finite_metadata.json').read_text());counts['finite_probe_masks']+=len(finite)
                steprows=rows(OUT/f'{name}_F_steps.csv');stepmap={(int(r['width_index']),int(r['penalty_floor']),r['probe_set'],int(r['step'])):r for r in steprows};summarymap={(int(r['width_index']),int(r['penalty_floor']),r['probe_set']):r for r in rows(OUT/f'{name}_F_summary.csv')}
                for wi,t in enumerate(old['width_upper_bounds']):
                  for li,floor in enumerate(old['lambda_lower_bounds']):
                   for label,length in [('F0',96),('F1',len(finite))]:
                    order=order_for(metadata[:length],t,floor);L0=r3['original_limit_prefix'][wi];Lp=r3['dense_limit_prefix'][wi];cum=np.zeros(n,bool);finite_counts=[0];union0=[L0.sum()];unionp=[Lp.sum()];overlaps=[0]
                    for step,k in enumerate(order,1):
                        new=finite[k]&~cum;cum|=finite[k];rr=stepmap[(wi,int(floor),label,step)];assert int(rr['archived_probe_index'])==k
                        vals=dict(marginal_new_finite=new.sum(),cumulative_finite=cum.sum(),cumulative_overlap_L0=(cum&L0).sum(),cumulative_overlap_Lplus=(cum&Lp).sum(),L0_unique_remaining=(L0&~cum).sum(),Lplus_unique_remaining=(Lp&~cum).sum(),cumulative_union_L0=(cum|L0).sum(),cumulative_union_Lplus=(cum|Lp).sum())
                        for key,value in vals.items():check(value,rr[key])
                        finite_counts.append(cum.sum());union0.append((cum|L0).sum());unionp.append((cum|Lp).sum());overlaps.append((cum&L0).sum());counts['cumulative_probe_rows']+=1
                    assert np.array_equal(cum,r3['finite_original' if label=='F0' else 'finite_all_archived'][wi,li]);rr=summarymap[(wi,int(floor),label)]
                    earliest=lambda seq:next(i for i,v in enumerate(seq) if v==seq[-1])
                    ef,e0,ep=map(earliest,[finite_counts,union0,unionp]);h95=next((i for i,v in enumerate(overlaps) if v>=.95*L0.sum()),None);h100=next((i for i,v in enumerate(overlaps) if v==L0.sum()),None)
                    vals=dict(eligible_archived_probes=len(order),finite_excluded=cum.sum(),L0_excluded=L0.sum(),Lplus_excluded=Lp.sum(),L0_unique=(L0&~cum).sum(),Lplus_unique=(Lp&~cum).sum(),earliest_prefix_final_finite=ef,earliest_prefix_final_union_L0=e0,earliest_prefix_final_union_Lplus=ep,retrospective_trailing_redundant_finite=len(order)-ef,retrospective_trailing_redundant_with_L0=len(order)-e0,retrospective_trailing_redundant_with_Lplus=len(order)-ep,zero_marginal_finite_probes=np.count_nonzero(np.diff(finite_counts)==0),actual_new_solves=0)
                    for key,value in vals.items():check(value,rr[key])
                    for key,value in [('probes_to_capture95pct_L0',h95),('probes_to_capture_all_L0',h100)]:
                        if value is None:assert rr[key]==''
                        else:check(value,rr[key])
                    allF.append(dict(dataset=ds,seed=seed,width_index=wi,penalty_floor=int(floor),probe_set=label,n=n,probes_to_capture95pct_L0=h95,probes_to_capture_all_L0=h100,**vals));counts['efficiency_regions']+=1
            counts['groups']+=1;print(name,'PASS',flush=True)
    # Aggregated F values, including missing-prefix availability denominators.
    for rr in rows(OUT/'F_aggregate.csv'):
        selected=[x for x in allF if x['dataset']==rr['dataset'] and x['width_index']==int(rr['width_index']) and x['penalty_floor']==int(rr['penalty_floor']) and x['probe_set']==rr['probe_set']];assert len(selected)==5
        for key in ['eligible_archived_probes','probes_to_capture95pct_L0','probes_to_capture_all_L0','earliest_prefix_final_finite','earliest_prefix_final_union_L0','earliest_prefix_final_union_Lplus','zero_marginal_finite_probes']:
            vals=[x[key] for x in selected if x[key] is not None];check(len(vals),rr[key+'_available_seeds'])
            if vals:check(np.mean(vals),rr[key+'_mean'])
            else:assert rr[key+'_mean']==''
            if len(vals)>1:check(np.std(vals,ddof=1),rr[key+'_sd'])
        for key in ['finite_excluded','L0_unique','Lplus_unique']:
            vals=[100*x[key]/x['n'] for x in selected];check(np.mean(vals),rr[key+'_mean_pct']);check(np.std(vals,ddof=1),rr[key+'_sd_pp'])
    for rr in rows(OUT/'D_summary.csv'):
        selected=[x for x in allD if x['dataset']==rr['dataset'] and x['K']==int(rr['K'])]
        for key in list(selected[0])[5:]:
            if key in ['maximum_sampled_sign_changes','bound_reference_index']:continue
            vals=[]
            for seed in [11,22,33,44,55]:
                ss=[x for x in selected if x['seed']==seed];vals.append(100*sum(x[key] for x in ss)/sum(x['n'] for x in ss))
            check(np.mean(vals),rr[key+'_mean_pct']);check(np.std(vals,ddof=1),rr[key+'_sd_pp'])
    report=dict(status='PASS',method='Independent raw-image/archived-weight replay; independent grouped ordering and all cumulative counts; no runner imports',counts=counts,new_fits=0,original_and_expanded_R3_unions_exact=True,elapsed_seconds=time.perf_counter()-start,script_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest())
    (HERE/'paths_efficiency_verification.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))

if __name__=='__main__':
    with threadpool_limits(1):main()
