#!/usr/bin/env python3
"""Independent v4 audit: no imports from archive certificate, runner or verifier.

Run from any directory. Reads the preserved archive; writes only --output.
Rebuilds geometry, all training majorants, all certificate masks, predictions
from stored weights, label scoring, finite checks, Table 2 and manifest checks.
An optional completed fresh original-runner output is compared array by array.
"""
import argparse, csv, gzip, hashlib, importlib.metadata, json, platform, sys, time
from pathlib import Path
from datetime import datetime, timezone
import numpy as np
from scipy.io import loadmat
from scipy.spatial.distance import cdist, pdist
from sklearn.model_selection import train_test_split
from threadpoolctl import threadpool_limits

METHODS = ('sharp','basic','cancellation_frobenius')

def sha(p):
    h=hashlib.sha256()
    with Path(p).open('rb') as f:
        for b in iter(lambda:f.read(1048576),b''):h.update(b)
    return h.hexdigest()

def readidx(path):
    raw=gzip.decompress(Path(path).read_bytes())
    assert raw[:2] == b'\x00\x00' and raw[2] == 8
    ndim=raw[3]; shape=np.frombuffer(raw,dtype='>i4',count=ndim,offset=4)
    data=np.frombuffer(raw,dtype=np.uint8,offset=4+4*ndim)
    assert data.size==int(np.prod(shape))
    return data.reshape(tuple(shape))

def writecsv(path,rows):
    with path.open('w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)

def check_manifest(root, path):
    d=json.loads(path.read_text())
    for rel,want in d.items():assert sha(root/rel)==want,rel
    return len(d)

def close(a,b,label,errors):
    assert np.allclose(a,b,rtol=2e-12,atol=2e-12,equal_nan=True),label
    finite=np.isfinite(a)&np.isfinite(b)
    e=float(np.max(np.abs(a[finite]-b[finite]))) if np.any(finite) else 0.
    errors[label]=max(errors.get(label,0.),e)

def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--baseline',type=Path,default=Path(__file__).resolve().parents[1]/'baseline')
    ap.add_argument('--output',type=Path,default=Path(__file__).resolve().parent)
    ap.add_argument('--fresh-results',type=Path)
    args=ap.parse_args();root=args.baseline.resolve();out=args.output.resolve();out.mkdir(parents=True,exist_ok=True)
    start=time.perf_counter();exp=root/'work/v2/experiment';results=exp/'results'
    p=json.loads((exp/'protocol.json').read_text());freeze=json.loads((exp/'FREEZE.json').read_text())
    report={'status':'RUNNING','audit_utc':datetime.now(timezone.utc).isoformat(),'baseline':str(root),'audit_script_sha256':sha(__file__),
            'environment':{'python':sys.version,'platform':platform.platform(),**{k:importlib.metadata.version(k) for k in ['numpy','scipy','scikit-learn','threadpoolctl']}}}
    report['manifests']={'package_files':check_manifest(root,root/'MANIFEST_SHA256.json'),
        'result_files':check_manifest(results,results/'MANIFEST_SHA256.json'),
        'prior_files':check_manifest(root/'work/controlled_study',root/'work/controlled_study/MANIFEST_SHA256.json')}
    report['freeze_hashes']={}
    for key,name in [('protocol_sha256','protocol.json'),('run_source_sha256','run_experiment.py'),('certificate_source_sha256','certificate.py'),('synthetic_checks_sha256','synthetic_checks.json')]:
        actual=sha(exp/name);assert actual==freeze[key],name;report['freeze_hashes'][name]=actual
    for rel,digest in p['data_sha256'].items():assert sha(root/rel)==digest,rel
    report['protocol_input_hashes_checked']=len(p['data_sha256'])
    mn=loadmat(root/'repository/Code/MNIST_train.mat');mnimg=mn['imagestrain'].transpose(2,0,1);mny=mn['labelstrain'].ravel().astype(int)
    canonical=root/'work/v2/design/canonical_mnist_images'
    assert np.array_equal(mnimg,readidx(canonical/'train-images-idx3-ubyte.gz'))
    assert np.array_equal(mny,readidx(canonical/'train-labels-idx1-ubyte.gz'))
    test=loadmat(root/'repository/Code/MNIST_test.mat')
    assert np.array_equal(test['images'].transpose(2,0,1),readidx(canonical/'t10k-images-idx3-ubyte.gz'))
    assert np.array_equal(test['labels'].ravel(),readidx(canonical/'t10k-labels-idx1-ubyte.gz'))
    reserve=np.load(root/'work/v2/design/reserved_training_ids.npy')
    old={};used=[]
    for seed in p['seeds']:
        with np.load(root/f'work/controlled_study/results/seed_{seed}_predictions.npz') as z:
            old[seed]={k:z[k].copy() for k in ['train_ids','validation_ids','center_ids']}
            used.extend([z['train_ids'],z['validation_ids']])
    union=np.unique(np.concatenate(used));assert np.array_equal(reserve,np.setdiff1d(np.arange(60000),union))
    report['provenance']={'mnist_train_and_test_canonical_image_label_equality':True,'prior_train_validation_union_n':len(union),
        'reserve_complement_exact':True,'reserve_n':len(reserve),'index_semantics':'zero-based original image index; Fashion query IDs index a separate official test array'}
    allfrozen=json.loads((results/'ALL_PREDICTIONS_FROZEN.json').read_text());complete=json.loads((results/'COMPLETE.json').read_text())
    assert allfrozen['heldout_truth_used'] is False and allfrozen['time_utc']<complete['finished_utc']
    receipts={(x['dataset'],x['seed'],x['K']):x for x in allfrozen['groups']}
    endpoint=[];coverage=[];groups=[];errors={};table=[];comparisons=[]
    totals={'groups':0,'endpoint_records':0,'certificate_records':0,'query_region_cases':0,'inapplicable_regions':0,
        'sharp_certified':0,'basic_certified':0,'cancellation_frobenius_certified':0,'sharp_probe_checks':0,
        'method_tagged_probe_checks':0,'deduplicated_probe_checks':0,'probe_violations':0,
        'recomputed_prediction_labels':0,'recomputed_prediction_mismatches':0,'factorizations':0,'fitted_readouts':0}
    margin_min=np.inf;ratio_min=np.inf
    with threadpool_limits(1):
        for dataset in p['datasets']:
            if dataset=='mnist':img=mnimg;ytrain=mny;qimg=img[reserve];yy=ytrain[reserve];qids=reserve
            else:
                d=root/'work/v2/data/fashion_mnist';img=readidx(d/'train-images-idx3-ubyte.gz');ytrain=readidx(d/'train-labels-idx1-ubyte.gz').astype(int)
                qimg=readidx(d/'t10k-images-idx3-ubyte.gz');yy=readidx(d/'t10k-labels-idx1-ubyte.gz');qids=np.arange(10000)
            assert np.array_equal(yy,np.load(results/f'{dataset}_evaluation_labels.npy'))
            Xq=qimg.transpose(0,2,1).reshape(len(qimg),-1).astype(float)/255
            for seed in p['seeds']:
                if dataset=='mnist':
                    tr=old[seed]['train_ids'];va=old[seed]['validation_ids'];lookup={int(v):i for i,v in enumerate(tr)}
                    prior=np.array([lookup[int(x)] for x in old[seed]['center_ids']]);available=np.setdiff1d(np.arange(len(tr)),prior)
                    rows200=np.r_[prior,np.random.default_rng(seed+p['mnist_extra_center_seed_offset']).choice(available,100,replace=False)]
                else:
                    tr,rem=train_test_split(np.arange(len(ytrain)),train_size=p['training_n'],stratify=ytrain,random_state=seed)
                    va,_=train_test_split(rem,train_size=p['validation_n'],stratify=ytrain[rem],random_state=seed+1000)
                    rows200=np.random.default_rng(seed).choice(len(tr),200,replace=False)
                assert not np.intersect1d(tr,va).size
                if dataset=='mnist':assert not np.intersect1d(np.r_[tr,va],reserve).size
                X=img[tr].transpose(0,2,1).reshape(len(tr),-1).astype(float)/255;Y=np.eye(10)[ytrain[tr]]
                for K in p['prototype_budgets']:
                    label=f'{dataset}_seed{seed}_K{K}';g=results/label;z=np.load(g/'predictions_before_labels.npz');rows=rows200[:K];C=X[rows];yc=ytrain[tr[rows]];Yc=np.eye(10)[yc]
                    for key,val in [('train_ids',tr),('validation_ids',va),('center_ids',tr[rows]),('center_rows',rows),('center_labels',yc),('query_ids',qids)]:assert np.array_equal(z[key],val),(label,key)
                    assert len(np.unique(C,axis=0))==K
                    receipt=json.loads((g/'PREDICTIONS_FROZEN.json').read_text());digest=sha(g/'predictions_before_labels.npz')
                    assert digest==receipt['sha256']==receipts[(dataset,seed,K)]['prediction_sha256']
                    assert receipt['reserved_truth_used'] is False and freeze['frozen_at_utc']<receipt['frozen_utc']<=allfrozen['time_utc']
                    scale=float(np.median(pdist(C))/np.sqrt(2));widths=np.r_[1.,np.array(p['width_multipliers'])*scale]
                    assert np.array_equal(widths,z['width_upper_bounds'])
                    Dt=cdist(X,C,'sqeuclidean');Dq=cdist(Xq,C,'sqeuclidean');nearest=np.argmin(Dq,axis=1);nn=yc[nearest]
                    assert np.array_equal(nn,z['nearest_prototype'])
                    order=np.sort(Dq,axis=1)[:,:2];unique=(order[:,1]-order[:,0])>p['nearest_tie_relative']*np.maximum(1,order[:,1])
                    masks=z['certificate_masks'];pred=z['predictions'];votes=z['prototype_votes'];pw=z['probe_widths'];ps=z['probe_penalties']
                    assert np.array_equal(pw,np.array(sorted({float(t*f) for t in widths for f in p['width_probe_fractions']})))
                    assert np.array_equal(ps,p['probe_penalties_union'])
                    assert np.array_equal(masks[:,:,0],masks[:,:,1]);assert np.all(~masks[:,:,2]|masks[:,:,1])
                    assert np.all(z['numerical_ranks']==K)
                    for pi,sigma in enumerate(pw):
                        rq=np.exp(-(Dq-Dq.min(axis=1)[:,None])/(2*sigma*sigma))
                        assert np.array_equal(np.argmax(rq@Yc,axis=1),votes[pi])
                        for lj in range(len(ps)):
                            rebuilt=np.argmax(rq@z['weights'][pi,lj],axis=1)
                            totals['recomputed_prediction_labels']+=len(yy);totals['recomputed_prediction_mismatches']+=int(np.sum(rebuilt!=pred[pi,lj]))
                    seen=np.zeros_like(pred,dtype=bool);gchecks=0;gbad=0
                    for wi,t in enumerate(widths):
                        H=np.exp(-Dt/(2*t*t));H[rows,np.arange(K)]=1;E=H.copy();E[rows,np.arange(K)]=0
                        non=np.ones(len(X),bool);non[rows]=False
                        V=E[rows]@Yc;P=E[non].T@Y[non];Q=E.T@(E@Yc);beta=float(E[rows].sum(axis=1).max());mu=max(1-beta,0)**2;eta=float(np.sqrt(np.square(E).sum()))
                        for key,val in [('V',V),('P',P),('Q',Q),('beta',np.array(beta)),('mu',np.array(mu))]:close(np.asarray(val),np.asarray(z[key][wi]),key,errors)
                        rq=np.exp(-(Dq-Dq.min(axis=1)[:,None])/(2*t*t));mass=rq@Yc;rn=np.sqrt(np.square(rq).sum(axis=1));lhs=1-mass;pi=int(np.flatnonzero(pw==t)[0])
                        for li,lo in enumerate(p['lambda_lower_bounds']):
                            b=np.full((3,10,10),np.inf);den=mu+lo;app=den>0
                            assert bool(z['certificate_applicable'][wi,li])==app
                            if app:
                                for a in range(10):
                                    for c in range(10):
                                        if a==c:b[:,a,c]=0;continue
                                        v=V[:,a]+V[:,c];pp=P[:,a]+P[:,c];q=Q[:,a]+Q[:,c]
                                        b[0,a,c]=max(np.sqrt(np.square((abs(lo-1)*v+(lo+1)*pp+q)/den).sum()),np.sqrt(np.square(v+pp).sum()))
                                        b[1,a,c]=np.sqrt(np.square(((lo+1)*(v+pp)+q)/den).sum())
                                        b[2,a,c]=((1+lo)*eta*np.sqrt(Y[:,a].sum()+Y[:,c].sum())+eta**2*np.sqrt(Yc[:,a].sum()+Yc[:,c].sum()))/den
                            close(b,z['pair_constants'][wi,li],'pair_constants',errors)
                            totals['inapplicable_regions']+=int(not app);totals['query_region_cases']+=len(yy)
                            lj=int(np.flatnonzero(ps==lo)[0]);pr=pred[pi,lj]
                            endpoint.append(dict(dataset=dataset,seed=seed,K=K,width_index=wi,lambda_lower=lo,n=len(yy),readout_correct=int(np.sum(pr==yy)),nearest_correct=int(np.sum(nn==yy)),vote_correct=int(np.sum(votes[pi]==yy)),nearest_readout_agree=int(np.sum(pr==nn)),vote_readout_agree=int(np.sum(pr==votes[pi])),nearest_wrong_readout_right=int(np.sum((nn!=yy)&(pr==yy))),nearest_right_readout_wrong=int(np.sum((nn==yy)&(pr!=yy)))))
                            probes=[(int(np.flatnonzero(pw==float(t*f))[0]),int(np.flatnonzero(ps==la)[0])) for f in p['width_probe_fractions'] for la in p['lambda_probe_rule'][str(lo)]]
                            for mi,method in enumerate(METHODS):
                                rhs=rn[:,None]*b[mi,nn,:];gap=lhs-rhs;guard=p['strict_guard']*(1+np.abs(lhs)+np.abs(rhs));ok=gap>guard;ok[np.arange(len(yy)),nn]=True
                                cm=unique&np.all(ok,axis=1);assert np.array_equal(cm,masks[wi,li,mi]),(label,wi,lo,method)
                                bad=sum(int(np.sum(cm&(pred[a,c]!=nn))) for a,c in probes);count=int(cm.sum());gchecks+=count*len(probes);gbad+=bad
                                coverage.append(dict(dataset=dataset,seed=seed,K=K,width_index=wi,lambda_lower=lo,method=method,n=len(yy),applicable=app,certified=count,coverage=count/len(yy),certified_probe_violations=bad))
                                totals[method+'_certified']+=count;totals['method_tagged_probe_checks']+=count*len(probes);totals['probe_violations']+=bad
                                if mi==0:
                                    totals['sharp_probe_checks']+=count*len(probes)
                                    for a,c in probes:seen[a,c]|=cm
                                if count:
                                    competing=np.ones_like(gap,dtype=bool);competing[np.arange(len(yy)),nn]=False;keep=competing&cm[:,None]
                                    margin_min=min(margin_min,float(gap[keep].min()));ratio_min=min(ratio_min,float((gap/guard)[keep].min()))
                    dedup=int(seen.sum());assert not np.any(seen&(pred!=nn));totals['deduplicated_probe_checks']+=dedup
                    groups.append(dict(dataset=dataset,seed=seed,K=K,n=len(yy),scale=scale,nearest_correct=int(np.sum(nn==yy)),train_n=len(tr),validation_n=len(va),distinct_prototypes=K,method_probe_checks=gchecks,method_probe_violations=gbad,deduplicated_probe_checks=dedup))
                    totals['groups']+=1;totals['factorizations']+=len(pw);totals['fitted_readouts']+=len(pw)*len(ps)
                    if args.fresh_results:
                        f=np.load(args.fresh_results/label/'predictions_before_labels.npz');exact=[];numerical=[]
                        for key in z.files:
                            if key=='factorization_seconds':continue
                            if z[key].dtype.kind in 'fc':close(z[key],f[key],'fresh_'+key,errors);numerical.append(key)
                            else:assert np.array_equal(z[key],f[key]),(label,key);exact.append(key)
                        comparisons.append(dict(group=label,exact_equal_arrays=exact,numerically_equal_arrays=numerical))
                    print(label,flush=True)
    totals['endpoint_records']=len(endpoint);totals['certificate_records']=len(coverage)
    assert totals['recomputed_prediction_mismatches']==0
    for fname,rows,fields in [('endpoint_accuracy_and_fidelity.csv',endpoint,['n','readout_correct','nearest_correct','vote_correct','nearest_readout_agree','vote_readout_agree','nearest_wrong_readout_right','nearest_right_readout_wrong']),('certificate_metrics_before_labels.csv',coverage,['n','certified','certified_probe_violations'])]:
        archived=list(csv.DictReader((results/fname).open()));assert len(archived)==len(rows)
        key=lambda r:(r['dataset'],int(r['seed']),int(r['K']),int(r['width_index']),int(float(r['lambda_lower'])),r.get('method',''))
        lookup={key(r):r for r in archived}
        for r in rows:
            for k in fields:assert int(lookup[key(r)][k])==r[k],(fname,key(r),k)
    for dataset in p['datasets']:
        for K in p['prototype_budgets']:
            for lo in p['lambda_lower_bounds']:
                row=dict(dataset=dataset,K=K,lambda_lower=lo)
                for method in METHODS:
                    vals=[r['coverage']*100 for r in coverage if r['dataset']==dataset and r['K']==K and r['lambda_lower']==lo and r['width_index']==1 and r['method']==method]
                    assert len(vals)==5;row[method+'_mean_pct']=float(np.mean(vals));row[method+'_sample_sd_pp']=float(np.std(vals,ddof=1));row[method+'_zero_seeds']=sum(x==0 for x in vals)
                table.append(row)
    assert all(r['certified']==0 for r in coverage if r['width_index']!=1)
    expected={'groups':30,'endpoint_records':630,'certificate_records':1890,'query_region_cases':4418505,'inapplicable_regions':102,'sharp_certified':587703,'basic_certified':587703,'cancellation_frobenius_certified':285286,'sharp_probe_checks':5289327,'method_tagged_probe_checks':13146228,'deduplicated_probe_checks':3585477,'probe_violations':0,'factorizations':480,'fitted_readouts':2880}
    for k,v in expected.items():assert totals[k]==v,(k,totals[k],v)
    report.update(status='PASS',counts=totals,checks={'all_masks_reconstructed_from_original_images':True,'stored_weights_reproduce_all_predictions':True,'all_endpoint_csv_counts_match':True,'all_certificate_csv_counts_match':True,'sharp_basic_masks_identical':True,'frobenius_masks_nested':True,'all_other_widths_zero':True,'all_center_selection_rules_exact':True,'all_splits_match':True,'all_prototype_images_distinct':True,'all_archived_ranks_full':True,'freeze_receipts_consistent':True},training_term_max_absolute_errors=errors,minimum_certified_margin=margin_min,minimum_certified_margin_guard_ratio=ratio_min,table2=table,group_records=groups,
        fresh_training_rerun={'performed':bool(args.fresh_results),'results':str(args.fresh_results) if args.fresh_results else None,'compared_groups':len(comparisons),'comparisons':comparisons},elapsed_seconds=time.perf_counter()-start)
    for name,rows in [('independent_endpoints.csv',endpoint),('independent_coverage.csv',coverage),('table2_reconstructed.csv',table),('independent_groups.csv',groups)]:writecsv(out/name,rows)
    (out/'independent_audit.json').write_text(json.dumps(report,indent=2,allow_nan=False)+'\n')
    print(json.dumps({'status':'PASS','counts':totals,'elapsed_seconds':report['elapsed_seconds']},indent=2))

if __name__=='__main__':main()
