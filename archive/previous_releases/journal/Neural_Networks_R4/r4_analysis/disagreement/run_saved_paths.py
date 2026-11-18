#!/usr/bin/env python3
"""Stages D/F: exact finite-grid replay. No readout fitting or source mutation."""
import argparse,csv,gzip,hashlib,json,sys,time
from pathlib import Path
import numpy as np
from scipy.io import loadmat
from scipy.spatial.distance import cdist
from threadpoolctl import threadpool_limits

HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[1]
BASE=ROOT/'evidence/baseline/evidence/baseline';EXP=BASE/'work/v2/experiment/results'
FRONT=ROOT/'evidence/baseline/evidence/frontier/results';DIAG=ROOT/'evidence/new_analysis/limit_diagnostic'
R3=ROOT/'r3_analysis/m1_m2/results'
PROTOCOL='53f0e8b55140eb90bcfae9901bac1540bc46a34a3698d38d02fdc7bbe5e72038'
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def js(p,x):p.write_text(json.dumps(x,indent=2,allow_nan=False)+'\n')
def csvwrite(p,rows):
    with p.open('w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
def flatten(a):return a.transpose(0,2,1).reshape(len(a),-1).astype(float)/255
def idx(p):return np.frombuffer(gzip.decompress(p.read_bytes()),np.uint8,offset=16).reshape(-1,28,28)
def scores(r,W,nn):
    s=r@W;p=s.argmax(1).astype(np.int8);n=s[np.arange(len(nn)),nn].copy();s[np.arange(len(nn)),nn]=-np.inf;c=s.max(1);d=c-n;g=1e-10*(1+abs(c)+abs(n));st=np.zeros(len(nn),np.int8);st[d>g]=1;st[d<-g]=-1;return d,g,st,p
def ordered_indices(metadata,t,floor):
    allowed=[i for i,m in enumerate(metadata) if m['width']<=t*(1+1e-14) and m['penalty']>=floor]
    allowed.sort(key=lambda i:(metadata[i]['width'],metadata[i]['penalty'],{'original':0,'frontier':1,'local_tail':2}[metadata[i]['source']],i))
    groups=[]
    for i in allowed:
        if not groups or not np.isclose(metadata[i]['width'],metadata[groups[-1][0]]['width'],rtol=1e-13,atol=0):groups.append([])
        groups[-1].append(i)
    return [g[j] for j in range(max(map(len,groups),default=0)) for g in groups if j<len(g)]

def group_run(dataset,seed,K,images,Xq,out):
    start=time.perf_counter();name=f'{dataset}_seed{seed}_K{K}';p=EXP/name/'predictions_before_labels.npz'
    with np.load(p) as z:
        C=flatten(images[z['center_ids']]);nn=z['nearest_prototype'];pw=z['probe_widths'];pl=z['probe_penalties'];weights=z['weights'];oldpred=z['predictions'];ranks=z['numerical_ranks'];widths=z['width_upper_bounds'];floors=z['lambda_lower_bounds'];qids=z['query_ids']
    D=cdist(Xq,C,'sqeuclidean');D-=D.min(1,keepdims=True);n=len(nn);shape=(len(pw),len(pl),n)
    margin=np.empty(shape);guard=np.empty(shape);state=np.empty(shape,np.int8);mismatch=0;finite=[];metadata=[]
    for wi,w in enumerate(pw):
        r=np.exp(-D/(2*w*w))
        for li,lam in enumerate(pl):
            dd,gg,st,pred=scores(r,weights[wi,li],nn)
            if lam==0 and ranks[wi]<K:st[:]=2
            margin[wi,li]=dd;guard[wi,li]=gg;state[wi,li]=st;mismatch+=int(np.count_nonzero(pred!=oldpred[wi,li]))
            finite.append(st==1);metadata.append(dict(width=float(w),penalty=float(lam),source='original',source_width_index=wi,source_penalty_index=li))
    assert mismatch==0
    first=np.full((len(pw),n),-1,np.int8);prev_agree=np.full_like(first,-1);first_lower=np.full((len(pw),n),np.nan);first_upper=first_lower.copy()
    changes=np.zeros_like(first);back=np.zeros_like(first);last_sign=np.zeros((len(pw),n),np.int8);ever_d=np.zeros((len(pw),n),bool)
    for li,lam in enumerate(pl):
        st=state[:,li];new=(st==1)&(first<0);first[new]=li;first_upper[new]=lam
        if li>0:first_lower[new]=pl[li-1]
        current_agree=(st==-1)&(first<0);prev_agree[current_agree]=li
        valid=(st==1)|(st==-1);changes+=((last_sign!=0)&valid&(st!=last_sign)).astype(np.int8)
        back+=((last_sign==1)&(st==-1)).astype(np.int8);last_sign[valid]=st[valid];ever_d|=(st==1)
    agree_all=np.all(state==-1,axis=1);guard_any=np.any(state==0,axis=1);invalid_any=np.any(state==2,axis=1)
    records=[];bounds=[];bound_map=np.full(len(pw),-1,np.int8);bound_arrays={}
    if K==100:
        with np.load(R3/f'{name}.npz') as z:
            bt=z['threshold'];bop=z['operator_norm'];bw=z['widths'];L0=z['original_limit_prefix'];Lp=z['dense_limit_prefix'];F0=z['finite_original'];F1=z['finite_all_archived']
        for wi,w in enumerate(pw):
            matched=np.flatnonzero(np.isclose(bw,w,rtol=1e-13,atol=0))
            if len(matched):bound_map[wi]=int(matched[0])
        bound_arrays=dict(bound_reference_widths=bw,bound_raw=bt,bound_operator_norm=bop)
    for wi,w in enumerate(pw):
        anyd=first[wi]>=0;left=first[wi]==0;pos=first[wi]>0;adj=np.zeros(n,bool);ii=np.flatnonzero(pos);adj[ii]=state[wi,first[wi,ii]-1,ii]==-1
        row=dict(dataset=dataset,seed=seed,K=K,width_index=wi,sigma=float(w),sigma_over_sC=float(w/(widths[1]*16)),n=n,strict_disagreement_any=int(anyd.sum()),left_censored_first_disagreement=int(left.sum()),first_detected_after_zero=int(pos.sum()),adjacent_strict_agreement_disagreement_bracket=int(adj.sum()),first_detection_guard_or_invalid_lower=int((pos&~adj).sum()),no_disagreement_observed=int((~anyd).sum()),strict_agreement_all_samples=int(agree_all[wi].sum()),no_disagreement_with_guard_samples=int((~anyd&guard_any[wi]).sum()),any_guard_sample=int(guard_any[wi].sum()),any_invalid_sample=int(invalid_any[wi].sum()),sampled_return_to_agreement=int((back[wi]>0).sum()),sampled_sign_changes_total=int(changes[wi].sum()),maximum_sampled_sign_changes=int(changes[wi].max()),bound_reference_index=int(bound_map[wi]))
        records.append(row)
        if bound_map[wi]>=0:
            bi=bound_map[wi];B=bt[bi];hasB=np.isfinite(B);firstlam=first_upper[wi];rp=anyd&hasB&(firstlam>0);ratio=B[rp]/firstlam[rp]
            guaranteed=(pl[:,None]>B[None,:]*(1+1e-10))&hasB[None,:]
            raw_failure=int(np.sum(guaranteed&(margin[wi]<=0)));guard_miss=int(np.sum(guaranteed&(state[wi]!=1)))
            assert raw_failure==0
            br=dict(dataset=dataset,seed=seed,K=K,probe_width_index=wi,bound_width_index=int(bi),sigma_over_sC=float(w/(widths[1]*16)),n=n,finite_bound_queries=int(hasB.sum()),no_finite_bound_queries=int((~hasB).sum()),observed_disagreement_with_finite_bound=int((anyd&hasB).sum()),observed_disagreement_without_finite_bound=int((anyd&~hasB).sum()),finite_bound_without_observed_disagreement=int((hasB&~anyd).sum()),first_observed_disagreement_below_bound=int((anyd&hasB&(firstlam<B)).sum()),finite_bound_above_largest_sampled_penalty=int((hasB&(B>pl[-1])).sum()),positive_first_penalty_ratio_cases=int(rp.sum()),bound_over_first_positive_penalty_median=float(np.median(ratio)) if len(ratio) else None,bound_over_first_positive_penalty_q90=float(np.quantile(ratio,.9)) if len(ratio) else None,grid_pairs_above_bound=int(guaranteed.sum()),above_bound_raw_margin_failures=raw_failure,above_bound_not_guarded_disagreement=guard_miss)
            bounds.append(br)
    np.savez_compressed(out/f'{name}_paths.npz',margin=margin,guard=guard,state=state,widths=pw,penalties=pl,nearest_prototype=nn,query_ids=qids,first_disagreement_index=first,last_strict_agreement_before_first=prev_agree,first_detection_lower_sample=first_lower,first_detection_upper_sample=first_upper,strict_agreement_all_samples=agree_all,any_guard_sample=guard_any,any_invalid_sample=invalid_any,sampled_sign_change_count=changes,sampled_return_to_agreement_count=back,bound_reference_index=bound_map,**bound_arrays)
    frec=[];fsummary=[]
    if K==100:
        n0=len(finite)
        with np.load(FRONT/name/'frontiers_before_labels.npz') as z:
            fw=z['widths'][z['fit_grid_indices']];fl=z['lambda_floors'];ww=z['weights'];rank=z['numerical_ranks'];preds=z['predictions']
        for wi,w in enumerate(fw):
            r=np.exp(-D/(2*w*w))
            for li,lam in enumerate(fl):
                _,_,st,pred=scores(r,ww[wi,li],nn);assert np.array_equal(pred,preds[wi,li])
                if lam==0 and rank[wi]<K:st[:]=2
                finite.append(st==1);metadata.append(dict(width=float(w),penalty=float(lam),source='frontier',source_width_index=wi,source_penalty_index=li))
        with np.load(DIAG/'local_tail_validation'/f'{name}.npz') as z,np.load(DIAG/'local_tail'/f'{name}.npz') as zz:
            for ri,rat in enumerate([.5,1.]):
                op=float(np.linalg.eigvalsh(zz[f'case{2*ri}_A_t'])[-1])
                for li,mul in enumerate([10,100]):
                    for si,frac in enumerate([.95,.99,1.]):
                        w=widths[1]*16*rat*frac;_,_,st,pred=scores(np.exp(-D/(2*w*w)),z[f't{ri}_weights'][li,si],nn);assert np.array_equal(pred,z[f't{ri}_predictions'][li,si])
                        finite.append(st==1);metadata.append(dict(width=float(w),penalty=float(mul*op),source='local_tail',source_width_index=ri*3+si,source_penalty_index=li))
        masks=np.array(finite);np.savez_compressed(out/f'{name}_finite_masks.npz',masks=masks,original_count=np.array(n0),widths=np.array([m['width'] for m in metadata]),penalties=np.array([m['penalty'] for m in metadata]),sources=np.array([m['source'] for m in metadata]),query_ids=qids,nearest_prototype=nn)
        js(out/f'{name}_finite_metadata.json',metadata)
        for wi,t in enumerate(widths):
          for li,fl in enumerate(floors):
           for label,limit in [('F0',n0),('F1',len(metadata))]:
            order=ordered_indices(metadata[:limit],t,float(fl));cum=np.zeros(n,bool);l0=L0[wi];lp=Lp[wi];cumcounts=[0];aug0=[int(l0.sum())];augp=[int(lp.sum())];hit95=0 if not l0.any() else None;hit100=0 if not l0.any() else None
            for step,ix in enumerate(order,1):
                m=masks[ix];new=m&~cum;cum|=m;over=int(np.sum(cum&l0));cumcounts.append(int(cum.sum()));aug0.append(int((cum|l0).sum()));augp.append(int((cum|lp).sum()))
                if hit95 is None and over>=.95*l0.sum():hit95=step
                if hit100 is None and over==l0.sum():hit100=step
                fr=dict(dataset=dataset,seed=seed,K=K,width_index=wi,sigma_over_sC=float(t/(widths[1]*16)),penalty_floor=int(fl),probe_set=label,n=n,step=step,archived_probe_index=ix,probe_width=float(metadata[ix]['width']),probe_penalty=float(metadata[ix]['penalty']),probe_source=metadata[ix]['source'],marginal_new_finite=int(new.sum()),cumulative_finite=int(cum.sum()),cumulative_overlap_L0=over,cumulative_overlap_Lplus=int((cum&lp).sum()),L0_unique_remaining=int((l0&~cum).sum()),Lplus_unique_remaining=int((lp&~cum).sum()),cumulative_union_L0=int((cum|l0).sum()),cumulative_union_Lplus=int((cum|lp).sum()))
                frec.append(fr)
            assert np.array_equal(cum,(F0 if label=='F0' else F1)[wi,li])
            ef=next(i for i,x in enumerate(cumcounts) if x==cumcounts[-1]);e0=next(i for i,x in enumerate(aug0) if x==aug0[-1]);ep=next(i for i,x in enumerate(augp) if x==augp[-1])
            fs=dict(dataset=dataset,seed=seed,K=K,width_index=wi,sigma_over_sC=float(t/(widths[1]*16)),penalty_floor=int(fl),probe_set=label,n=n,eligible_archived_probes=len(order),finite_excluded=int(cum.sum()),L0_excluded=int(l0.sum()),Lplus_excluded=int(lp.sum()),L0_unique=int((l0&~cum).sum()),Lplus_unique=int((lp&~cum).sum()),probes_to_capture95pct_L0=hit95,probes_to_capture_all_L0=hit100,earliest_prefix_final_finite=ef,earliest_prefix_final_union_L0=e0,earliest_prefix_final_union_Lplus=ep,retrospective_trailing_redundant_finite=len(order)-ef,retrospective_trailing_redundant_with_L0=len(order)-e0,retrospective_trailing_redundant_with_Lplus=len(order)-ep,zero_marginal_finite_probes=sum(cumcounts[i]==cumcounts[i-1] for i in range(1,len(cumcounts))),actual_new_solves=0)
            fsummary.append(fs)
    csvwrite(out/f'{name}_D_per_width.csv',records)
    if bounds:csvwrite(out/f'{name}_D_bounds.csv',bounds)
    if frec:csvwrite(out/f'{name}_F_steps.csv',frec);csvwrite(out/f'{name}_F_summary.csv',fsummary)
    info=dict(group=name,runtime_seconds=time.perf_counter()-start,prediction_mismatches=mismatch,query_parameter_predictions=int(np.prod(shape)),path_cases=len(pw)*n,original_archive_sha256=sha(p),new_solves=0)
    js(out/f'{name}_COMPLETE.json',info);return info

def summarize(out):
    paths=sorted(out.glob('*_D_per_width.csv'));D=[r for p in paths for r in csv.DictReader(p.open())];B=[r for p in sorted(out.glob('*_D_bounds.csv')) for r in csv.DictReader(p.open())];F=[r for p in sorted(out.glob('*_F_summary.csv')) for r in csv.DictReader(p.open())]
    csvwrite(out/'D_per_width.csv',D);csvwrite(out/'D_bounds.csv',B);csvwrite(out/'F_summary.csv',F)
    dg=[]
    metrics=[m for m in D[0] if m not in ['dataset','seed','K','width_index','sigma','sigma_over_sC','n','bound_reference_index','maximum_sampled_sign_changes']]
    for ds in ['mnist','fashion_mnist']:
     for K in [50,100,200]:
      for seed in [11,22,33,44,55]:
        rr=[r for r in D if r['dataset']==ds and int(r['K'])==K and int(r['seed'])==seed];r=dict(dataset=ds,seed=seed,K=K,query_width_cases=sum(int(x['n']) for x in rr))
        for m in metrics:r[m]=sum(int(x[m]) for x in rr)
        r['maximum_sampled_sign_changes']=max(int(x['maximum_sampled_sign_changes']) for x in rr);dg.append(r)
    csvwrite(out/'D_per_group.csv',dg);summary=[]
    for ds in ['mnist','fashion_mnist']:
     for K in [50,100,200]:
        rr=[r for r in dg if r['dataset']==ds and r['K']==K];r=dict(dataset=ds,K=K,seeds=len(rr),query_width_cases_per_seed=rr[0]['query_width_cases'])
        for m in metrics:
            v=np.array([q[m]/q['query_width_cases']*100 for q in rr]);r[m+'_mean_pct']=float(v.mean());r[m+'_sd_pp']=float(v.std(ddof=1))
        summary.append(r)
    csvwrite(out/'D_summary.csv',summary)
    s=[]
    for ds in ['mnist','fashion_mnist']:
     for wi in range(7):
      for floor in [0,1,100]:
       for ps in ['F0','F1']:
        rr=[r for r in F if r['dataset']==ds and int(r['width_index'])==wi and int(r['penalty_floor'])==floor and r['probe_set']==ps];r=dict(dataset=ds,width_index=wi,sigma_over_sC_mean=float(np.mean([float(x['sigma_over_sC']) for x in rr])),penalty_floor=floor,probe_set=ps,seeds=len(rr))
        for field in ['eligible_archived_probes','probes_to_capture95pct_L0','probes_to_capture_all_L0','earliest_prefix_final_finite','earliest_prefix_final_union_L0','earliest_prefix_final_union_Lplus','zero_marginal_finite_probes']:
            v=[float(x[field]) for x in rr if x[field]!=''];r[field+'_available_seeds']=len(v);r[field+'_mean']=float(np.mean(v)) if v else None;r[field+'_sd']=float(np.std(v,ddof=1)) if len(v)>1 else None
        for field in ['finite_excluded','L0_unique','Lplus_unique']:
            v=[100*int(x[field])/int(x['n']) for x in rr];r[field+'_mean_pct']=float(np.mean(v));r[field+'_sd_pp']=float(np.std(v,ddof=1))
        s.append(r)
    csvwrite(out/'F_aggregate.csv',s)

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--pilot',action='store_true');ap.add_argument('--recompute',action='store_true',help='Reconstruct every group even when saved checkpoints exist.');args=ap.parse_args();assert sha(HERE/'protocol.json')==PROTOCOL
    out=HERE/'results';out.mkdir(exist_ok=True);start=time.perf_counter();groups=[]
    with threadpool_limits(1):
      for ds in ['mnist','fashion_mnist']:
        if ds=='mnist':
            z=loadmat(BASE/'repository/Code/MNIST_train.mat',variable_names=['imagestrain']);images=z['imagestrain'].transpose(2,0,1);qimages=images[np.load(BASE/'work/v2/design/reserved_training_ids.npy')]
        else:
            folder=BASE/'work/v2/data/fashion_mnist';images=idx(folder/'train-images-idx3-ubyte.gz');qimages=idx(folder/'t10k-images-idx3-ubyte.gz')
        Xq=flatten(qimages)
        for seed in [11,22,33,44,55]:
         for K in [50,100,200]:
            if args.pilot and (ds!='mnist' or seed!=11 or K!=100):continue
            name=f'{ds}_seed{seed}_K{K}';receipt=out/f'{name}_COMPLETE.json'
            if receipt.exists() and not args.recompute:info=json.loads(receipt.read_text());info['reused_checkpoint']=True
            else:info=group_run(ds,seed,K,images,Xq,out)
            groups.append(info);print(json.dumps(info),flush=True)
    if args.pilot:
        js(HERE/'PILOT.json',dict(groups=groups,elapsed_seconds=time.perf_counter()-start,estimated_remaining_seconds=groups[0]['runtime_seconds']*29,interpretation='One K100 MNIST group; estimate is arithmetic planning only, not a measured total.'));return
    assert len(groups)==30;summarize(out)
    js(out/'COMPLETE.json',dict(status='PASS',protocol_sha256=PROTOCOL,runner_sha256=sha(Path(__file__)),elapsed_this_run_seconds=time.perf_counter()-start,total_group_runtime_seconds=sum(x['runtime_seconds'] for x in groups),new_solves=0,groups=groups,python=sys.version,numpy=np.__version__,original_prediction_mismatches=sum(g['prediction_mismatches'] for g in groups),original_prediction_comparisons=sum(g['query_parameter_predictions'] for g in groups)))
    js(out/'SHA256_MANIFEST.json',{str(p.relative_to(out)):sha(p) for p in sorted(out.iterdir()) if p.is_file() and p.name!='SHA256_MANIFEST.json'})

if __name__=='__main__':main()
