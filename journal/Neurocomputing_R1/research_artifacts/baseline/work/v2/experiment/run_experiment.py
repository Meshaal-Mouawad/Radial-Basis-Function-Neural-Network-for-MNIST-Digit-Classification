#!/usr/bin/env python3
"""Prospective continuum-faithfulness experiment. No execution without frozen receipt."""
import argparse,csv,gzip,hashlib,json,platform,struct,time,sys
from datetime import datetime,timezone
from pathlib import Path
import numpy as np
from scipy.io import loadmat
from scipy.linalg import svd
from scipy.spatial.distance import cdist,pdist
from sklearn.model_selection import train_test_split
from threadpoolctl import threadpool_limits,threadpool_info
from certificate import training_terms,constants,query_certificate,query_features,METHODS

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[2]

def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def js(p,x):Path(p).write_text(json.dumps(x,indent=2,allow_nan=False)+'\n')
def csvwrite(p,rows):
    if not rows:return
    with Path(p).open('w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(dict.fromkeys(k for r in rows for k in r)));w.writeheader();w.writerows(rows)
def idx_images(p):
    b=gzip.decompress(Path(p).read_bytes());magic,n,r,c=struct.unpack('>IIII',b[:16]);assert magic==2051
    return np.frombuffer(b,np.uint8,offset=16).reshape(n,r,c)
def idx_labels(p):
    b=gzip.decompress(Path(p).read_bytes());magic,n=struct.unpack('>II',b[:8]);assert magic==2049
    return np.frombuffer(b,np.uint8,offset=8).copy()
def flatten(X):return X.transpose(0,2,1).reshape(len(X),-1).astype(np.float64)/255

def data_load(name,p):
    if name=='mnist':
        d=loadmat(ROOT/'repository/Code/MNIST_train.mat')
        images=d['imagestrain'].transpose(2,0,1)
        labels=d['labelstrain'].ravel().astype(np.int64)
        reserve=np.load(ROOT/'work/v2/design/reserved_training_ids.npy')
        return images,labels,images[reserve],reserve
    folder=ROOT/'work/v2/data/fashion_mnist'
    return idx_images(folder/'train-images-idx3-ubyte.gz'),idx_labels(folder/'train-labels-idx1-ubyte.gz').astype(np.int64),idx_images(folder/'t10k-images-idx3-ubyte.gz'),np.arange(10000)

def eval_labels(name):
    if name=='mnist':
        y=loadmat(ROOT/'repository/Code/MNIST_train.mat',variable_names=['labelstrain'])['labelstrain'].ravel()
        return y[np.load(ROOT/'work/v2/design/reserved_training_ids.npy')]
    return idx_labels(ROOT/'work/v2/data/fashion_mnist/t10k-labels-idx1-ubyte.gz')

def split_centers(name,y,seed,p):
    if name=='mnist':
        with np.load(ROOT/f'work/controlled_study/results/seed_{seed}_predictions.npz') as z:
            train=z['train_ids'];val=z['validation_ids'];old=z['center_ids']
        rows={int(v):i for i,v in enumerate(train)}
        centers100=np.asarray([rows[int(v)] for v in old])
        available=np.setdiff1d(np.arange(len(train)),centers100)
        extras=np.random.default_rng(seed+p['mnist_extra_center_seed_offset']).choice(available,100,False)
        centers200=np.concatenate([centers100,extras])
    else:
        train,remaining=train_test_split(np.arange(len(y)),train_size=p['training_n'],stratify=y,random_state=seed)
        val,unused=train_test_split(remaining,train_size=p['validation_n'],stratify=y[remaining],random_state=seed+1000)
        centers200=np.random.default_rng(seed).choice(len(train),200,False)
    assert not np.intersect1d(train,val).size
    return train,val,centers200

def fit_from_factor(s,vt,uty,lam,n):
    if lam==0:
        f=np.zeros_like(s);keep=s>max(n,len(s))*np.finfo(float).eps*s[0];f[keep]=1/s[keep]
    else:f=s/(s*s+lam)
    return vt.T@(f[:,None]*uty)

def self_tests():
    rng=np.random.default_rng(202611061);count=0;certified=0;violations=0;max_dominance=0.
    for trial in range(20):
        X=rng.normal(size=(45,3));y=rng.integers(0,4,45);rows=rng.choice(45,8,False);C=X[rows];Y=np.eye(4)[y];Z=np.vstack([C+.001,rng.normal(size=(17,3))]);D=cdist(Z,C,'sqeuclidean')
        for t in [.1,.4,1.]:
            H=np.exp(-cdist(X,C,'sqeuclidean')/(2*t*t));terms=training_terms(H,Y,rows)
            for lam0 in [0.,1.,100.]:
                b,app=constants(terms,lam0);cert,ref,gaps,unique=query_certificate(D,Y[rows],t,b)
                if app:max_dominance=max(max_dominance,float(np.max(b[0]-b[1])))
                assert np.all(~cert[1]|cert[0]) and np.all(~cert[2]|cert[1])
                certified+=int(cert.sum());count+=len(Z)
                for frac in [.5,.75,1.]:
                    sig=t*frac;hs=np.exp(-cdist(X,C,'sqeuclidean')/(2*sig*sig));hs[rows,np.arange(8)]=1
                    u,s,vt=svd(hs,full_matrices=False);uty=u.T@Y
                    for lam in sorted(set([lam0,max(1.,10*lam0),max(100.,100*lam0)])):
                        W=fit_from_factor(s,vt,uty,lam,len(X));pred=np.argmax(query_features(D,sig)@W,axis=1)
                        violations+=int(np.sum(cert&(pred[None,:]!=ref[None,:])))
    assert violations==0 and max_dominance<1e-9
    # Duplicate inputs carrying contradictory labels disprove an unconditional NN limit.
    X=np.array([[0.],[0.],[0.],[3.]]);y=np.array([0,1,1,1]);r=np.array([0,3]);C=X[r];Y=np.eye(2)[y];D=cdist(np.array([[0.]]),C,'sqeuclidean');H=np.exp(-cdist(X,C,'sqeuclidean')/(2*.01**2));terms=training_terms(H,Y,r);b,_=constants(terms,1.);cert,ref,_,_=query_certificate(D,Y[r],.01,b);W=np.linalg.solve(H.T@H+np.eye(2),H.T@Y);pred=int(np.argmax(query_features(D,.01)@W));assert pred==1 and ref[0]==0 and not cert.any()
    # Equal nearest distances always abstain under the declared policy.
    _,_,_,unique=query_certificate(np.array([[1.,1.]]),np.eye(2),1.,np.zeros((3,2,2)));assert not unique[0]
    return {'synthetic_query_rectangles':count,'certified_method_query_rectangles':certified,'certified_violations':violations,'max_sharp_minus_basic_constant':max_dominance,'contradictory_duplicate':'PASS','nearest_tie_abstention':'PASS'}

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--protocol',type=Path,default=HERE/'protocol.json');ap.add_argument('--freeze',type=Path,default=HERE/'FREEZE.json');ap.add_argument('--output-dir',type=Path);ap.add_argument('--self-test-only',action='store_true');ap.add_argument('--execute',action='store_true');args=ap.parse_args()
    if args.self_test_only:
        ans=self_tests();js(HERE/'synthetic_checks.json',ans);print(json.dumps(ans));return
    if not args.execute:raise SystemExit('No training performed. A frozen protocol and --execute are required.')
    p=json.loads(args.protocol.read_text());receipt=json.loads(args.freeze.read_text())
    assert p['status']=='frozen' and sha(args.protocol)==receipt['protocol_sha256']
    assert sha(__file__)==receipt['run_source_sha256'] and sha(HERE/'certificate.py')==receipt['certificate_source_sha256']
    out=args.output_dir.resolve();assert not out.exists() or not any(out.iterdir()),'Use a new empty output directory';out.mkdir(parents=True,exist_ok=True)
    for rel,h in p['data_sha256'].items():assert sha(ROOT/rel)==h,rel
    checks=self_tests();js(out/'preflight.json',checks);js(out/'environment.json',{'started_utc':datetime.now(timezone.utc).isoformat(),'python':sys.version,'platform':platform.platform(),'numpy':np.__version__,'threads':threadpool_info(),'freeze':receipt})
    metricrows=[];diagrows=[];group_paths=[];completion=[];totalstart=time.perf_counter()
    with threadpool_limits(1):
        for dataset in p['datasets']:
            images,train_labels,query_images,query_ids=data_load(dataset,p);Xq=flatten(query_images)
            for seed in p['seeds']:
                tids,vids,c200=split_centers(dataset,train_labels,seed,p)
                if dataset=='mnist':assert not np.intersect1d(tids,query_ids).size and not np.intersect1d(vids,query_ids).size
                X=flatten(images[tids]);y=train_labels[tids];Y=np.eye(10)[y]
                for K in p['prototype_budgets']:
                    start=time.perf_counter();rows=c200[:K];C=X[rows];Yc=Y[rows];yc=y[rows];scale=float(np.median(pdist(C))/np.sqrt(2));widths=np.array([1.]+[scale*x for x in p['width_multipliers']]);lows=p['lambda_lower_bounds'];penalties=p['probe_penalties_union'];fractions=p['width_probe_fractions']
                    tdist=time.perf_counter();Dt=cdist(X,C,'sqeuclidean');Dq=cdist(Xq,C,'sqeuclidean');disttime=time.perf_counter()-tdist
                    distinct_prototypes=int(len(np.unique(C,axis=0)));minimum_center_distance=float(np.min(pdist(C)))
                    nearest=np.argmin(Dq,axis=1);nn=yc[nearest]
                    probe_widths=np.array(sorted(set(float(t*f) for t in widths for f in fractions)))
                    termslist=[];allbounds=[];masks=np.zeros((len(widths),len(lows),3,len(Xq)),bool);min_gaps=np.zeros_like(masks,dtype=float);applies=np.zeros((len(widths),len(lows)),bool);boundtimes=[]
                    for wi,t in enumerate(widths):
                        ts=time.perf_counter();H=np.exp(-Dt/(2*t*t));H[rows,np.arange(K)]=1.;terms=training_terms(H,Y,rows);termslist.append(terms);bws=[]
                        for li,lo in enumerate(lows):
                            b,app=constants(terms,lo);m,ref,g,u=query_certificate(Dq,Yc,t,b,p['strict_guard'],p['nearest_tie_relative']);assert np.array_equal(ref,nn);assert np.all(~m[1]|m[0]) and np.all(~m[2]|m[1]);masks[wi,li]=m;min_gaps[wi,li]=g;applies[wi,li]=app;bws.append(b)
                        allbounds.append(bws);boundtimes.append(time.perf_counter()-ts)
                        diagrows.append({'dataset':dataset,'seed':seed,'K':K,'width_index':wi,'upper_sigma':t,'scale':scale,'beta':terms['beta'],'mu':terms['mu'],'E_frobenius':terms['eta'],'distinct_prototype_images':distinct_prototypes,'minimum_center_distance':minimum_center_distance,'train_activation_median':float(np.median(H)),'train_activation_below_1e12':float(np.mean(H<1e-12)),'distance_seconds_shared':disttime,'certificate_precompute_and_queries_seconds_all_lower_bounds':boundtimes[-1]})
                    predictions=np.empty((len(probe_widths),len(penalties),len(Xq)),np.int8);votes=np.empty((len(probe_widths),len(Xq)),np.int8);weights=np.empty((len(probe_widths),len(penalties),K,10));factimes=[];fitted_singular=[];numerical_ranks=[]
                    for pi,sigma in enumerate(probe_widths):
                        H=np.exp(-Dt/(2*sigma*sigma));H[rows,np.arange(K)]=1.;Hq=query_features(Dq,sigma);votes[pi]=np.argmax(Hq@Yc,axis=1);ts=time.perf_counter();u,s,vt=svd(H,full_matrices=False,check_finite=False);uty=u.T@Y;factimes.append(time.perf_counter()-ts);fitted_singular.append([float(s[0]),float(s[-1])]);numerical_ranks.append(int(np.sum(s>max(len(X),len(s))*np.finfo(float).eps*s[0])))
                        for lj,lam in enumerate(penalties):
                            W=fit_from_factor(s,vt,uty,lam,len(X));weights[pi,lj]=W;predictions[pi,lj]=np.argmax(Hq@W,axis=1)
                    group=out/f'{dataset}_seed{seed}_K{K}';group.mkdir()
                    np.savez_compressed(group/'predictions_before_labels.npz',dataset=dataset,seed=seed,K=K,train_ids=tids,validation_ids=vids,center_ids=tids[rows],center_rows=rows,center_labels=yc,query_ids=query_ids,width_upper_bounds=widths,lambda_lower_bounds=lows,probe_widths=probe_widths,probe_penalties=penalties,predictions=predictions,prototype_votes=votes,nearest_prototype=nn,certificate_masks=masks,certificate_min_gaps=min_gaps,certificate_applicable=applies,pair_constants=np.asarray(allbounds),weights=weights,V=np.asarray([z['V'] for z in termslist]),P=np.asarray([z['P'] for z in termslist]),Q=np.asarray([z['Q'] for z in termslist]),beta=np.asarray([z['beta'] for z in termslist]),mu=np.asarray([z['mu'] for z in termslist]),factorization_seconds=factimes,singular_extremes=fitted_singular,numerical_ranks=numerical_ranks)
                    predhash=sha(group/'predictions_before_labels.npz');violation=0
                    for wi,t in enumerate(widths):
                        for li,lo in enumerate(lows):
                            lp=p['lambda_probe_rule'][str(lo)];probe_indices=[(int(np.argmin(abs(probe_widths-t*f))),penalties.index(la)) for f in fractions for la in lp]
                            for mi,name in enumerate(METHODS):
                                cm=masks[wi,li,mi];bad=sum(int(np.sum(cm&(predictions[a,b]!=nn))) for a,b in probe_indices);violation+=bad
                                metricrows.append({'dataset':dataset,'seed':seed,'K':K,'width_index':wi,'sigma_upper':float(t),'lambda_lower':lo,'method':name,'n':len(Xq),'applicable':bool(applies[wi,li]),'certified':int(cm.sum()),'coverage':float(cm.mean()),'probe_pairs':len(probe_indices),'certified_probe_violations':bad,'prediction_archive_sha256':predhash})
                    js(group/'PREDICTIONS_FROZEN.json',{'frozen_utc':datetime.now(timezone.utc).isoformat(),'sha256':predhash,'reserved_truth_used':False,'violations':violation,'runtime_seconds':time.perf_counter()-start})
                    assert violation==0,'Certified disagreement found; preserve and investigate'
                    group_paths.append((dataset,group));completion.append({'dataset':dataset,'seed':seed,'K':K,'seconds':time.perf_counter()-start,'prediction_sha256':predhash});csvwrite(out/'certificate_metrics_before_labels.csv',metricrows);csvwrite(out/'feature_diagnostics.csv',diagrows);js(out/'progress.json',completion);print(json.dumps(completion[-1]),flush=True)
        js(out/'ALL_PREDICTIONS_FROZEN.json',{'time_utc':datetime.now(timezone.utc).isoformat(),'groups':completion,'heldout_truth_used':False})
        # Only now index evaluation targets and compute truth metrics; all model/mask archives are immutable.
        # MNIST labels were loaded for training; reserved entries were never indexed for fitting or metrics.
        accuracies=[];cert_accuracy=[]
        for dataset in p['datasets']:
            yy=eval_labels(dataset);np.save(out/f'{dataset}_evaluation_labels.npy',yy)
            for name,group in group_paths:
                if name!=dataset:continue
                with np.load(group/'predictions_before_labels.npz') as z:
                    pred=z['predictions'];nn=z['nearest_prototype'];vote=z['prototype_votes'];masks=z['certificate_masks'];ws=z['width_upper_bounds'];pw=z['probe_widths'];ps=z['probe_penalties'];los=z['lambda_lower_bounds'];seed=int(z['seed']);K=int(z['K']);assert pred.shape[-1]==len(yy)
                    for wi,t in enumerate(ws):
                        pi=int(np.argmin(abs(pw-t)))
                        for li,lo in enumerate(los):
                            lj=int(np.flatnonzero(ps==lo)[0]);pr=pred[pi,lj];agree=pr==nn
                            base={'dataset':dataset,'seed':seed,'K':K,'width_index':wi,'sigma_upper':float(t),'lambda_lower':float(lo),'n':len(yy)}
                            accuracies.append(dict(base,readout_correct=int(np.sum(pr==yy)),nearest_correct=int(np.sum(nn==yy)),vote_correct=int(np.sum(vote[pi]==yy)),nearest_readout_agree=int(agree.sum()),vote_readout_agree=int(np.sum(pr==vote[pi])),nearest_wrong_readout_right=int(np.sum((nn!=yy)&(pr==yy))),nearest_right_readout_wrong=int(np.sum((nn==yy)&(pr!=yy)))))
                            for mi,method in enumerate(METHODS):
                                cm=masks[wi,li,mi];cert_accuracy.append(dict(base,method=method,certified=int(cm.sum()),certified_correct=int(np.sum(cm&(pr==yy))),uncertified_correct=int(np.sum(~cm&(pr==yy))),actual_agreements=int(agree.sum()),certified_among_agreements=int(np.sum(cm&agree))))
        csvwrite(out/'endpoint_accuracy_and_fidelity.csv',accuracies);csvwrite(out/'certificate_accuracy.csv',cert_accuracy);js(out/'COMPLETE.json',{'finished_utc':datetime.now(timezone.utc).isoformat(),'total_seconds':time.perf_counter()-totalstart,'groups':len(group_paths),'certificate_rows':len(metricrows),'endpoint_rows':len(accuracies),'certified_probe_violations':sum(r['certified_probe_violations'] for r in metricrows),'source_hashes':receipt})
        manifest={str(q.relative_to(out)):sha(q) for q in sorted(out.rglob('*')) if q.is_file() and q.name!='MANIFEST_SHA256.json'};js(out/'MANIFEST_SHA256.json',manifest)
    print(json.dumps({'status':'COMPLETE','groups':len(group_paths),'runtime_seconds':time.perf_counter()-totalstart}),flush=True)
if __name__=='__main__':main()
