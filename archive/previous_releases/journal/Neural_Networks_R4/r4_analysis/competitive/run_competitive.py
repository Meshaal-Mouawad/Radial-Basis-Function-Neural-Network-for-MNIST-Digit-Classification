#!/usr/bin/env python3
"""R4 E/G: validation-only selections and no-fit operating-region reconstruction."""
import argparse,csv,gzip,hashlib,importlib.util,json,platform,struct,time
from pathlib import Path
import numpy as np
from scipy.io import loadmat
from scipy.spatial.distance import cdist
from threadpoolctl import threadpool_limits
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def js(p,x):p.write_text(json.dumps(x,indent=2,allow_nan=False)+'\n')
def csvwrite(p,rows):
    with p.open('w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
def imgs(p):
    b=gzip.decompress(p.read_bytes());_,n,h,w=struct.unpack('>IIII',b[:16]);return np.frombuffer(b,np.uint8,offset=16).reshape(n,h,w)
def flat(x):return x.transpose(0,2,1).reshape(len(x),-1).astype(float)/255.
def opposing(scores,nn):
    own=scores[np.arange(len(nn)),nn];other=scores.copy();other[np.arange(len(nn)),nn]=-np.inf;mx=other.max(1)
    return mx-own>1e-10*(1+abs(mx)+abs(own))
def jaccard(a,b):
    union=(a|b).sum();return float((a&b).sum()/union) if union else 1.

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--evidence',type=Path,default=ROOT/'evidence');ap.add_argument('--output',type=Path,default=HERE/'results');ap.add_argument('--pilot',action='store_true');a=ap.parse_args()
    evidence=a.evidence.resolve();out=a.output.resolve();out.mkdir(parents=True,exist_ok=True);base=evidence/'baseline/evidence/baseline';exp=base/'work/v2/experiment/results'
    certpath=base/'work/v2/experiment/certificate.py';spec=importlib.util.spec_from_file_location('frozen_certificate',certpath);mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod)
    protocolsha=sha(HERE/'protocol.json');runnersha=sha(Path(__file__));start=time.perf_counter();groupinfo=[];allhashes={};surface=[];bestrows=[];setrows=[];classrows=[];groups={};reconstructed=0;certificate_crosschecks=0
    with threadpool_limits(1):
      for ds in ['mnist','fashion_mnist']:
        if ds=='mnist':
            f=base/'repository/Code/MNIST_train.mat';d=loadmat(f);images=d['imagestrain'].transpose(2,0,1);labels=d['labelstrain'].ravel().astype(int);qimages=images[np.load(base/'work/v2/design/reserved_training_ids.npy')];datafiles=[f,base/'work/v2/design/reserved_training_ids.npy']
        else:
            f=base/'work/v2/data/fashion_mnist';images=imgs(f/'train-images-idx3-ubyte.gz');qimages=imgs(f/'t10k-images-idx3-ubyte.gz');labels=np.frombuffer(gzip.decompress((f/'train-labels-idx1-ubyte.gz').read_bytes()),np.uint8,offset=8).astype(int);datafiles=[f/n for n in ['train-images-idx3-ubyte.gz','t10k-images-idx3-ubyte.gz','train-labels-idx1-ubyte.gz']]
        datafiles += [certpath,exp/f'{ds}_evaluation_labels.npy'];datahashes={str(p.relative_to(evidence)):sha(p) for p in datafiles};allhashes.update(datahashes);Xq=flat(qimages)
        for seed in [11,22,33,44,55]:
          for K in [50,100,200]:
            name=f'{ds}_seed{seed}_K{K}';f=exp/name/'predictions_before_labels.npz';inputsha=sha(f);allhashes[str(f.relative_to(evidence))]=inputsha;npzpath=out/f'{name}.npz';receiptpath=out/f'{name}.json';gstart=time.perf_counter()
            cached=False
            if npzpath.exists() and receiptpath.exists():
                receipt=json.loads(receiptpath.read_text());cached=(receipt['input_sha256']==inputsha and receipt['protocol_sha256']==protocolsha and receipt['runner_sha256']==runnersha and receipt['data_hashes']==datahashes and receipt['npz_sha256']==sha(npzpath))
                if not cached:raise RuntimeError(f'Stale checkpoint {name}; inspect before replacing')
            if not cached:
                with np.load(f) as z:
                    train=z['train_ids'];valid=z['validation_ids'];centers=z['center_ids'];centerrows=z['center_rows'];yc=z['center_labels'];qid=z['query_ids'];nn=z['nearest_prototype'];pw=z['probe_widths'];pl=z['probe_penalties'];W=z['weights'];ranks=z['numerical_ranks'];pred=z['predictions'];ow=z['width_upper_bounds'];of=z['lambda_lower_bounds'];oldcert=z['certificate_masks'][:,:,0];scale=float(ow[1]*16)
                assert not np.intersect1d(train,valid).size
                if ds=='mnist':assert not np.intersect1d(train,qid).size and not np.intersect1d(valid,qid).size
                C=flat(images[centers]);Dt=cdist(flat(images[train]),C,'sqeuclidean');Dv=cdist(flat(images[valid]),C,'sqeuclidean');Dq=cdist(Xq,C,'sqeuclidean');Y=np.eye(10)[labels[train]];Yc=np.eye(10)[yc];n=len(nn)
                valpred=np.empty((len(pw),len(pl),len(valid)),np.int8);valcorrect=np.zeros((len(pw),len(pl)),int);cert=np.empty((len(pw),len(pl),n),bool);finite=np.empty_like(cert);limit=np.empty((len(pw),n),bool);mismatch=0;matches=0
                for wi,w in enumerate(pw):
                    rq=mod.query_features(Dq,w);rv=mod.query_features(Dv,w);H=np.exp(-Dt/(2*w*w));H[centerrows,np.arange(K)]=1.;terms=mod.training_terms(H,Y,centerrows);Z=H.T@Y;limit[wi]=opposing(rq@Z,nn)
                    for li,lam in enumerate(pl):
                        vp=(rv@W[wi,li]).argmax(1);valpred[wi,li]=vp;valcorrect[wi,li]=np.sum(vp==labels[valid]);score=rq@W[wi,li];mismatch+=int(np.count_nonzero(score.argmax(1)!=pred[wi,li]));finite[wi,li]=opposing(score,nn)
                        if lam==0 and ranks[wi]<K:finite[wi,li]=False
                        b,_=mod.constants(terms,lam);cm,ref,_,_=mod.query_certificate(Dq,Yc,w,b);assert np.array_equal(ref,nn);cert[wi,li]=cm[0];assert not np.any(cert[wi,li]&(pred[wi,li]!=nn))
                        wmatch=np.flatnonzero(np.isclose(ow,w,rtol=1e-13,atol=0));lmatch=np.flatnonzero(of==lam)
                        if len(wmatch) and len(lmatch):assert np.array_equal(cert[wi,li],oldcert[wmatch[0],lmatch[0]]);matches+=1
                assert mismatch==0 and matches==21
                best=int(valcorrect.reshape(-1).argmax());bwi,bli=np.unravel_index(best,valcorrect.shape);bestcount=valcorrect.max();competitive=np.array([valcorrect>=q*bestcount for q in [.90,.95,.99]])
                # Frozen validation selection precedes first indexing of evaluation truth.
                truth=np.load(exp/f'{ds}_evaluation_labels.npy');assert len(truth)==n
                prefix=np.logical_or.accumulate(limit,axis=0);finite_region=np.empty_like(finite)
                for wi in range(len(pw)):
                    for li,lam in enumerate(pl):finite_region[wi,li]=np.any(finite[:wi+1,pl>=lam],axis=(0,1))
                excluded=finite_region|prefix[:,None,:];assert not np.any(cert&excluded)
                np.savez_compressed(npzpath,validation_ids=valid,validation_truth=labels[valid],validation_predictions=valpred,validation_correct=valcorrect,competitive=competitive,thresholds=np.array([.90,.95,.99]),best_width_index=bwi,best_penalty_index=bli,probe_widths=pw,probe_penalties=pl,scale=scale,query_ids=qid,truth=truth,nearest_prototype=nn,predictions=pred,certificate=cert,limit_endpoint=limit,limit_prefix=prefix,finite_endpoint=finite,finite_region=finite_region,excluded_region=excluded)
                receipt=dict(group=name,input_sha256=inputsha,protocol_sha256=protocolsha,runner_sha256=runnersha,data_hashes=datahashes,npz_sha256=sha(npzpath),seconds=time.perf_counter()-gstart,reconstructed_prediction_labels=int(pred.size),validation_score_evaluations=int(valcorrect.size),certificate_original_mask_matches=matches,prediction_mismatch=0,certificate_violations=0,certificate_exclusion_intersections=0,new_fits=0)
                js(receiptpath,receipt)
            groupinfo.append(dict(receipt,cached=cached));reconstructed+=receipt['reconstructed_prediction_labels'];certificate_crosschecks+=receipt['certificate_original_mask_matches'];print(json.dumps({'group':name,'seconds':receipt['seconds'],'cached':cached,'progress':len(groupinfo), 'estimated_remaining_seconds':float(np.mean([x['seconds'] for x in groupinfo])*(30-len(groupinfo)))}),flush=True)
            if a.pilot:
                js(out/'PILOT.json',groupinfo[-1]);return
            with np.load(npzpath) as z:
                vc=z['validation_correct'];vN=len(z['validation_ids']);pw=z['probe_widths'];pl=z['probe_penalties'];scale=float(z['scale']);pred=z['predictions'];truth=z['truth'];nn=z['nearest_prototype'];qid=z['query_ids'];cert=z['certificate'];ex=z['excluded_region'];nf=z['finite_region'];lp=z['limit_prefix'];comp=z['competitive'];bwi=int(z['best_width_index']);bli=int(z['best_penalty_index']);n=len(truth)
                correct=pred==truth;agreement=pred==nn
                for wi,w in enumerate(pw):
                    for li,lam in enumerate(pl):
                        c=cert[wi,li];surface.append(dict(dataset=ds,seed=seed,K=K,width_index=wi,penalty_index=li,sigma=float(w),sigma_over_sC=float(w/scale),penalty=int(lam),validation_n=vN,validation_correct=int(vc[wi,li]),validation_accuracy_pct=float(vc[wi,li]/vN*100),validation_best=bool(wi==bwi and li==bli),competitive90=bool(comp[0,wi,li]),competitive95=bool(comp[1,wi,li]),competitive99=bool(comp[2,wi,li]),evaluation_n=n,evaluation_accuracy_pct=float(correct[wi,li].mean()*100),nearest_accuracy_pct=float(np.mean(nn==truth)*100),nearest_agreement_pct=float(agreement[wi,li].mean()*100),certified=int(c.sum()),certificate_coverage_pct=float(c.mean()*100),certified_accuracy_pct=float(correct[wi,li,c].mean()*100) if c.any() else None,limit_prefix_exclusion_pct=float(lp[wi].mean()*100),finite_region_exclusion_pct=float(nf[wi,li].mean()*100),combined_region_exclusion_pct=float(ex[wi,li].mean()*100),unresolved_region_pct=float((~ex[wi,li]&~c).mean()*100)))
                br=dict(next(x for x in surface[-96:] if x['validation_best']));bestrows.append(br)
                for qi,q in enumerate([.90,.95,.99]):
                    selected=comp[qi];sr=dict(dataset=ds,seed=seed,K=K,threshold=q,retained_models=int(selected.sum()),best_validation_accuracy_pct=float(vc.max()/vN*100),all_retained_zero_coverage=bool(not cert[selected].any()),certified_query_model_count=int(cert[selected].sum()),any_retained_certified_queries=int(cert[selected].any(axis=0).sum()))
                    for field,values in [('validation_accuracy_pct',vc/vN*100),('evaluation_accuracy_pct',correct.mean(2)*100),('agreement_pct',agreement.mean(2)*100),('certificate_coverage_pct',cert.mean(2)*100),('region_exclusion_pct',ex.mean(2)*100)]:
                        vals=values[selected];sr[field+'_min']=float(vals.min());sr[field+'_mean']=float(vals.mean());sr[field+'_max']=float(vals.max())
                    setrows.append(sr)
                bestpred=pred[bwi,bli];groups[(ds,seed,K)]={'pred':bestpred,'correct':bestpred==truth,'cert':cert[bwi,bli],'qid':qid,'truth':truth,'nn':nn,'validation_ids':z['validation_ids'],'best':br}
                for k in range(10):
                    tr=truth==k;pr=bestpred==k;classrows.append(dict(dataset=ds,seed=seed,K=K,class_label=k,evaluation_class_count=int(tr.sum()),predicted_count=int(pr.sum()),correct_count=int((tr&pr).sum()),recall_pct=float((tr&pr).sum()/tr.sum()*100),prediction_share_pct=float(pr.mean()*100),certified_class_count=int((tr&cert[bwi,bli]).sum())))
    csvwrite(out/'surface_per_model.csv',surface);csvwrite(out/'validation_best_per_seed.csv',bestrows);csvwrite(out/'competitive_sets_per_seed.csv',setrows);csvwrite(out/'validation_best_class_counts.csv',classrows)
    summaries=[];setsumm=[];paired=[];cross=[]
    for ds in ['mnist','fashion_mnist']:
      for K in [50,100,200]:
        rr=[x for x in bestrows if x['dataset']==ds and x['K']==K];s=dict(dataset=ds,K=K,seeds=5)
        for field in ['validation_accuracy_pct','evaluation_accuracy_pct','nearest_accuracy_pct','nearest_agreement_pct','certificate_coverage_pct','combined_region_exclusion_pct','sigma_over_sC','penalty']:
            values=[r[field] for r in rr];s[field+'_mean']=float(np.mean(values));s[field+'_sd']=float(np.std(values,ddof=1))
        summaries.append(s)
        for q in [.90,.95,.99]:
            rr=[x for x in setrows if x['dataset']==ds and x['K']==K and x['threshold']==q];s=dict(dataset=ds,K=K,threshold=q,seeds=5,retained_models_total=sum(x['retained_models'] for x in rr),groups_all_zero_coverage=sum(x['all_retained_zero_coverage'] for x in rr),certified_query_model_count=sum(x['certified_query_model_count'] for x in rr))
            for field in ['retained_models','evaluation_accuracy_pct_mean','agreement_pct_mean','certificate_coverage_pct_mean','region_exclusion_pct_mean']:
                vals=[x[field] for x in rr];s[field+'_mean']=float(np.mean(vals));s[field+'_sd']=float(np.std(vals,ddof=1))
            setsumm.append(s)
        for i,s1 in enumerate([11,22,33,44,55]):
          for s2 in [11,22,33,44,55][i+1:]:
            x=groups[(ds,s1,K)];y=groups[(ds,s2,K)];assert np.array_equal(x['qid'],y['qid']) and np.array_equal(x['truth'],y['truth']);cross.append(dict(dataset=ds,K=K,seed1=s1,seed2=s2,shared_evaluation_queries=len(x['qid']),prediction_disagreement_pct=float(np.mean(x['pred']!=y['pred'])*100),correctness_jaccard=jaccard(x['correct'],y['correct']),certificate_jaccard=jaccard(x['cert'],y['cert']),correct_both=int((x['correct']&y['correct']).sum()),validation_id_overlap=int(len(np.intersect1d(x['validation_ids'],y['validation_ids'])))))
      for seed in [11,22,33,44,55]:
        for ka,kb in [(50,100),(100,200),(50,200)]:
            x=groups[(ds,seed,ka)];y=groups[(ds,seed,kb)];assert np.array_equal(x['qid'],y['qid']);row=dict(dataset=ds,seed=seed,K_low=ka,K_high=kb,paired_evaluation_queries=len(x['qid']),evaluation_accuracy_difference_pp=y['best']['evaluation_accuracy_pct']-x['best']['evaluation_accuracy_pct'],validation_accuracy_difference_pp=y['best']['validation_accuracy_pct']-x['best']['validation_accuracy_pct'],nearest_agreement_difference_pp=y['best']['nearest_agreement_pct']-x['best']['nearest_agreement_pct'],prediction_disagreement_pct=float(np.mean(x['pred']!=y['pred'])*100),correctness_jaccard=jaccard(x['correct'],y['correct']),correct_high_only=int((y['correct']&~x['correct']).sum()),correct_low_only=int((x['correct']&~y['correct']).sum()),certificate_jaccard=jaccard(x['cert'],y['cert']));paired.append(row)
    pairsumm=[]
    for ds in ['mnist','fashion_mnist']:
      for ka,kb in [(50,100),(100,200),(50,200)]:
        rr=[x for x in paired if x['dataset']==ds and x['K_low']==ka and x['K_high']==kb];s=dict(dataset=ds,K_low=ka,K_high=kb,seeds=5)
        for field in ['evaluation_accuracy_difference_pp','validation_accuracy_difference_pp','nearest_agreement_difference_pp','prediction_disagreement_pct','correctness_jaccard']:
            vals=[x[field] for x in rr];s[field+'_mean']=float(np.mean(vals));s[field+'_sd']=float(np.std(vals,ddof=1))
        s['seeds_positive_accuracy_difference']=sum(x['evaluation_accuracy_difference_pp']>0 for x in rr);pairsumm.append(s)
    csvwrite(out/'validation_best_summary.csv',summaries);csvwrite(out/'competitive_sets_summary.csv',setsumm);csvwrite(out/'budget_paired_per_seed.csv',paired);csvwrite(out/'budget_paired_summary.csv',pairsumm);csvwrite(out/'cross_seed_stability.csv',cross)
    js(out/'COMPLETE.json',dict(status='PASS',groups=30,archived_models=2880,validation_predictions=30*96*5000,reconstructed_evaluation_predictions=reconstructed,certificate_original_mask_matches=certificate_crosschecks,new_fits=0,all_group_receipts=groupinfo,inputs_sha256=allhashes,protocol_sha256=protocolsha,runner_sha256=runnersha,certificate_source_sha256=sha(certpath),runtime_seconds_this_invocation=time.perf_counter()-start,runtime_seconds_groups=sum(x['seconds'] for x in groupinfo),numpy=np.__version__,platform=platform.platform(),unique_evaluation_query_counts={'mnist':4027,'fashion_mnist':10000},shared_query_handling='Per-seed metrics and paired query masks only, no independence assumption or inferential tests.'))
    js(out/'MANIFEST_SHA256.json',{p.name:sha(p) for p in sorted(out.iterdir()) if p.is_file() and p.name!='MANIFEST_SHA256.json'})
    print(json.dumps({'status':'PASS','groups':30,'runtime':time.perf_counter()-start}),flush=True)
if __name__=='__main__':main()
