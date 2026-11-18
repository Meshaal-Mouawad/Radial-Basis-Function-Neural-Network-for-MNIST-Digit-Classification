"""Read-only independent verification of the completed v2 experiment."""
from pathlib import Path
import json,csv,hashlib,gzip,struct
from datetime import datetime
import numpy as np
from scipy.io import loadmat
ROOT=Path(__file__).resolve().parents[3]; E=ROOT/'work/v2/experiment'; R=E/'results';OUT=Path(__file__).resolve().parent
assert (R/'COMPLETE.json').is_file()
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
p=json.loads((E/'protocol.json').read_text());freeze=json.loads((E/'FREEZE.json').read_text());complete=json.loads((R/'COMPLETE.json').read_text());manifest=json.loads((R/'MANIFEST_SHA256.json').read_text())
for key,path in [('protocol_sha256',E/'protocol.json'),('run_source_sha256',E/'run_experiment.py'),('certificate_source_sha256',E/'certificate.py')]:assert sha(path)==freeze[key]
for path,h in manifest.items():assert sha(R/path)==h,path
for path,h in p['data_sha256'].items():assert sha(ROOT/path)==h,path
allfreeze=json.loads((R/'ALL_PREDICTIONS_FROZEN.json').read_text());alltime=datetime.fromisoformat(allfreeze['time_utc']);assert alltime<datetime.fromisoformat(complete['finished_utc'])
assert len(allfreeze['groups'])==30 and allfreeze['heldout_truth_used'] is False
# Verify saved targets against the declared raw evaluation datasets after completion.
labels={d:np.load(R/f'{d}_evaluation_labels.npy') for d in p['datasets']}
res=np.load(ROOT/'work/v2/design/reserved_training_ids.npy')
my=loadmat(ROOT/'repository/Code/MNIST_train.mat',variable_names=['labelstrain'])['labelstrain'].ravel()
assert np.array_equal(labels['mnist'],my[res])
fb=gzip.decompress((ROOT/'work/v2/data/fashion_mnist/t10k-labels-idx1-ubyte.gz').read_bytes());magic,fn=struct.unpack('>II',fb[:8]);assert magic==2049 and fn==10000;assert np.array_equal(labels['fashion_mnist'],np.frombuffer(fb,np.uint8,offset=8))
with (R/'endpoint_accuracy_and_fidelity.csv').open() as f:arows=list(csv.DictReader(f))
with (R/'certificate_accuracy.csv').open() as f:crows=list(csv.DictReader(f))
with (R/'certificate_metrics_before_labels.csv').open() as f:mrows=list(csv.DictReader(f))
def key(x,method=False):
 z=(x['dataset'],int(x['seed']),int(x['K']),int(x['width_index']),int(float(x['lambda_lower'])))
 return z+(x['method'],) if method else z
A={key(x):x for x in arows};C={key(x,True):x for x in crows};M={key(x,True):x for x in mrows}
assert len(A)==len(arows)==630 and len(C)==len(crows)==1890 and len(M)==len(mrows)==1890
methods=['sharp','basic','cancellation_frobenius'];groups=[];seen={};checks=0;condition_checks=0;violationtotal=0;certified_exposures=0;allmargins=[];finite_all_min=float('inf');finite_all_max=-float('inf');ranks=[];modelcount=0;factorcount=0;max_order_excess=[-float('inf')]*2;fullfinite=True
for dataset in p['datasets']:
 for seed in p['seeds']:
  for K in p['prototype_budgets']:
   group=R/f'{dataset}_seed{seed}_K{K}';path=group/'predictions_before_labels.npz';rec=json.loads((group/'PREDICTIONS_FROZEN.json').read_text());assert rec['sha256']==sha(path);assert rec['reserved_truth_used'] is False;assert datetime.fromisoformat(rec['frozen_utc'])<=alltime
   with np.load(path) as z:
    assert str(z['dataset'])==dataset and int(z['seed'])==seed and int(z['K'])==K
    tids=z['train_ids'];vids=z['validation_ids'];cid=z['center_ids'];crow=z['center_rows'];qid=z['query_ids'];assert len(tids)==20000 and len(vids)==5000 and len(cid)==K;assert len(np.unique(cid))==K;assert np.array_equal(tids[crow],cid);assert not np.intersect1d(tids,vids).size
    if dataset=='mnist':assert np.array_equal(qid,res);assert not np.intersect1d(tids,qid).size and not np.intersect1d(vids,qid).size
    else:assert np.array_equal(qid,np.arange(10000))
    if K==50:seen[(dataset,seed)]=cid.copy()
    else:assert np.array_equal(cid[:len(seen[(dataset,seed)])],seen[(dataset,seed)]);seen[(dataset,seed)]=cid.copy()
    if dataset=='mnist' and K==100:
     with np.load(ROOT/f'work/controlled_study/results/seed_{seed}_predictions.npz') as old:assert np.array_equal(cid,old['center_ids']) and np.array_equal(tids,old['train_ids']) and np.array_equal(vids,old['validation_ids'])
    yy=labels[dataset];pw=z['probe_widths'];ps=z['probe_penalties'];ws=z['width_upper_bounds'];los=z['lambda_lower_bounds'];pred=z['predictions'];nn=z['nearest_prototype'];vote=z['prototype_votes'];masks=z['certificate_masks'];gaps=z['certificate_min_gaps'];app=z['certificate_applicable'];b=z['pair_constants'];assert pred.shape==(len(pw),len(ps),len(yy));modelcount+=len(pw)*len(ps);factorcount+=len(pw)
    assert np.array_equal(ps,p['probe_penalties_union']) and np.array_equal(los,p['lambda_lower_bounds'])
    assert np.all(~masks[:,:,1,:]|masks[:,:,0,:]);assert np.all(~masks[:,:,2,:]|masks[:,:,1,:]);assert np.all(~masks[~app])
    for j in range(2):
     valid=np.isfinite(b[:,:,j])&np.isfinite(b[:,:,j+1]);ex=(b[:,:,j]-b[:,:,j+1])[valid];max_order_excess[j]=max(max_order_excess[j],float(ex.max()))
     assert np.all(ex<=1e-10*(1+np.abs(b[:,:,j+1][valid])))
    assert np.all(np.isfinite(z['weights']));ranks.extend(z['numerical_ranks'].tolist())
    gm=gaps[masks];allmargins.extend(gm.tolist());assert np.all(np.isfinite(gm)) and np.all(gm>1e-10)
    finite=gaps[np.isfinite(gaps)];finite_all_min=min(finite_all_min,float(finite.min()));finite_all_max=max(finite_all_max,float(finite.max()))
    # Certified regions must be nested over increasing upper widths and penalty floors.
    wiorder=np.argsort(ws)
    for i in range(1,len(wiorder)):assert np.all(~masks[wiorder[i]]|masks[wiorder[i-1]])
    for i in range(1,len(los)):assert np.all(~masks[:,i-1]|masks[:,i])
    for wi,t in enumerate(ws):
     pi=np.flatnonzero(pw==t);assert len(pi)==1;pi=int(pi[0])
     for li,lo in enumerate(los):
      lj=np.flatnonzero(ps==lo);assert len(lj)==1;lj=int(lj[0]);pr=pred[pi,lj];agree=pr==nn;k=(dataset,seed,K,wi,int(lo))
      actual={'n':len(yy),'readout_correct':int(np.sum(pr==yy)),'nearest_correct':int(np.sum(nn==yy)),'vote_correct':int(np.sum(vote[pi]==yy)),'nearest_readout_agree':int(agree.sum()),'vote_readout_agree':int(np.sum(pr==vote[pi])),'nearest_wrong_readout_right':int(np.sum((nn!=yy)&(pr==yy))),'nearest_right_readout_wrong':int(np.sum((nn==yy)&(pr!=yy)))}
      for field,val in actual.items():assert int(A[k][field])==val,(k,field)
      assert float(A[k]['sigma_upper'])==t
      ix=[]
      for frac in p['width_probe_fractions']:
       v=np.flatnonzero(pw==float(t*frac));assert len(v)==1
       for la in p['lambda_probe_rule'][str(int(lo))]:
        a=np.flatnonzero(ps==la);assert len(a)==1;ix.append((int(v[0]),int(a[0])))
      assert len(ix)==9 and len(set(ix))==9
      for mi,name in enumerate(methods):
       cm=masks[wi,li,mi];kk=k+(name,);count=int(cm.sum());bad=sum(int(np.sum(cm&(pred[a,b]!=nn))) for a,b in ix)
       violationtotal+=bad;certified_exposures+=count*len(ix)
       truth={'certified':count,'certified_correct':int(np.sum(cm&(pr==yy))),'uncertified_correct':int(np.sum(~cm&(pr==yy))),'actual_agreements':int(agree.sum()),'certified_among_agreements':int(np.sum(cm&agree))}
       for field,val in truth.items():assert int(C[kk][field])==val,(kk,field)
       assert int(M[kk]['n'])==len(yy) and int(M[kk]['certified'])==count and float(M[kk]['coverage'])==count/len(yy) and int(M[kk]['probe_pairs'])==9 and int(M[kk]['certified_probe_violations'])==bad and M[kk]['prediction_archive_sha256']==sha(path) and (M[kk]['applicable']=='True')==bool(app[wi,li])
       checks+=1
      condition_checks+=1
    groups.append({'dataset':dataset,'seed':seed,'K':K,'probe_widths':len(pw),'fitted_models':len(pw)*len(ps),'minimum_numerical_rank':int(z['numerical_ranks'].min()),'expected_K':K,'certified_entries':int(masks.sum()),'minimum_certified_margin':float(gm.min()) if len(gm) else None,'maximum_certified_margin':float(gm.max()) if len(gm) else None})
assert violationtotal==complete['certified_probe_violations']==0
assert checks==1890 and condition_checks==630
# All original checksums still match after the read-only computation.
assert all(sha(R/q)==h for q,h in manifest.items())
result={'status':'PASS','source_freeze_hashes':'PASS','data_hashes_checked':len(p['data_sha256']),'result_manifest_entries_checked':len(manifest),'prediction_archive_groups':len(groups),'all_group_receipts_precede_global_frozen_receipt':True,'evaluation_targets_match_raw_declared_data':True,'endpoint_csv_rows_recomputed':condition_checks,'certificate_csv_rows_recomputed':checks,'certificate_before_labels_rows_recomputed':checks,'fitted_readouts_archived':modelcount,'feature_factorizations_archived':factorcount,'certified_probe_exposures':certified_exposures,'certified_probe_violations':violationtotal,'exact_probe_indexing':'PASS','split_and_nested_centers':'PASS','bound_and_mask_ordering':'PASS','bandwidth_and_penalty_mask_nesting':'PASS','max_sharp_minus_basic_constant':max_order_excess[0],'max_basic_minus_count_constant':max_order_excess[1],'minimum_certified_raw_margin':min(allmargins),'maximum_certified_raw_margin':max(allmargins),'minimum_finite_all_raw_margin':finite_all_min,'maximum_finite_all_raw_margin':finite_all_max,'groups':groups}
(OUT/'completed_experiment_audit.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps({k:v for k,v in result.items() if k!='groups'},indent=2))
