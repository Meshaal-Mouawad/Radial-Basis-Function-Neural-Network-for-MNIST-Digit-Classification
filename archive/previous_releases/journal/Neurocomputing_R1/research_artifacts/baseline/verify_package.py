#!/usr/bin/env python3
"""Verify this evidence package without fitting a model or modifying any file."""
import argparse,csv,hashlib,json
from pathlib import Path

ROOT=Path(__file__).resolve().parent

def sha(path):
    h=hashlib.sha256()
    with path.open('rb') as f:
        for chunk in iter(lambda:f.read(1048576),b''):h.update(chunk)
    return h.hexdigest()

def check_manifest(root,name='MANIFEST_SHA256.json'):
    manifest=json.loads((root/name).read_text())
    for rel,digest in manifest.items():
        p=root/rel
        if not p.is_file() or sha(p)!=digest:raise AssertionError(f'Hash mismatch or missing file: {p.relative_to(ROOT)}')
    return len(manifest)

def predictions():
    import numpy as np
    R=ROOT/'work/v2/experiment/results'
    p=json.loads((ROOT/'work/v2/experiment/protocol.json').read_text())
    with (R/'endpoint_accuracy_and_fidelity.csv').open() as f:endpoints=list(csv.DictReader(f))
    with (R/'certificate_metrics_before_labels.csv').open() as f:certrows=list(csv.DictReader(f))
    table={(r['dataset'],int(r['seed']),int(r['K']),int(r['width_index']),int(float(r['lambda_lower']))):r for r in endpoints}
    ctable={(r['dataset'],int(r['seed']),int(r['K']),int(r['width_index']),int(float(r['lambda_lower'])),r['method']):r for r in certrows}
    methods=('sharp','basic','cancellation_frobenius');counts={'groups':0,'endpoint_records':0,'certificate_records':0,'certified_probe_checks':0,'violations':0}
    for dataset in p['datasets']:
        y=np.load(R/f'{dataset}_evaluation_labels.npy',allow_pickle=False)
        for seed in p['seeds']:
            for K in p['prototype_budgets']:
                g=R/f'{dataset}_seed{seed}_K{K}'
                with np.load(g/'predictions_before_labels.npz',allow_pickle=False) as z:
                    tids,vids,cids=z['train_ids'],z['validation_ids'],z['center_ids']
                    assert not np.intersect1d(tids,vids).size and set(cids)<=set(tids)
                    if dataset=='mnist':assert not np.intersect1d(tids,z['query_ids']).size and not np.intersect1d(vids,z['query_ids']).size
                    masks=z['certificate_masks'];pred=z['predictions'];nn=z['nearest_prototype'];vote=z['prototype_votes'];pw=z['probe_widths'];ps=z['probe_penalties']
                    assert np.all(~masks[:,:,1,:]|masks[:,:,0,:]) and np.all(~masks[:,:,2,:]|masks[:,:,1,:])
                    for wi,t in enumerate(z['width_upper_bounds']):
                        pi=np.flatnonzero(pw==t);assert len(pi)==1;pi=int(pi[0])
                        for li,lo in enumerate(z['lambda_lower_bounds']):
                            lj=np.flatnonzero(ps==lo);assert len(lj)==1;lj=int(lj[0]);pr=pred[pi,lj]
                            row=table[(dataset,seed,K,wi,int(lo))]
                            actual={'n':len(y),'readout_correct':int(np.sum(pr==y)),'nearest_correct':int(np.sum(nn==y)),'vote_correct':int(np.sum(vote[pi]==y)),'nearest_readout_agree':int(np.sum(pr==nn)),'vote_readout_agree':int(np.sum(pr==vote[pi])),'nearest_wrong_readout_right':int(np.sum((nn!=y)&(pr==y))),'nearest_right_readout_wrong':int(np.sum((nn==y)&(pr!=y)))}
                            for k,v in actual.items():assert int(row[k])==v,(dataset,seed,K,wi,lo,k)
                            counts['endpoint_records']+=1
                            indices=[]
                            for fraction in p['width_probe_fractions']:
                                a=np.flatnonzero(pw==float(t*fraction));assert len(a)==1
                                for lam in p['lambda_probe_rule'][str(int(lo))]:
                                    b=np.flatnonzero(ps==lam);assert len(b)==1;indices.append((int(a[0]),int(b[0])))
                            for mi,method in enumerate(methods):
                                cm=masks[wi,li,mi];cr=ctable[(dataset,seed,K,wi,int(lo),method)];assert int(cm.sum())==int(cr['certified'])
                                bad=sum(int(np.sum(cm&(pred[a,b]!=nn))) for a,b in indices)
                                assert bad==int(cr['certified_probe_violations'])==0
                                counts['certificate_records']+=1;counts['certified_probe_checks']+=int(cm.sum())*len(indices);counts['violations']+=bad
                    counts['groups']+=1
    assert counts['groups']==30 and counts['endpoint_records']==630 and counts['certificate_records']==1890
    return counts

def main():
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--predictions',action='store_true',help='Also recompute all declared endpoint and finite certificate checks; requires NumPy.');args=ap.parse_args()
    report={'package_files_checked':check_manifest(ROOT)}
    exp=ROOT/'work/v2/experiment';freeze=json.loads((exp/'FREEZE.json').read_text());protocol=json.loads((exp/'protocol.json').read_text())
    for key,name in [('protocol_sha256','protocol.json'),('run_source_sha256','run_experiment.py'),('certificate_source_sha256','certificate.py')]:assert sha(exp/name)==freeze[key],name
    for rel,h in protocol['data_sha256'].items():assert sha(ROOT/rel)==h,rel
    report['frozen_inputs_checked']=len(protocol['data_sha256']);report['v2_result_files_checked']=check_manifest(exp/'results');report['prior_study_files_checked']=check_manifest(ROOT/'work/controlled_study')
    if args.predictions:report['prediction_recomputation']=predictions()
    report['status']='PASS';print(json.dumps(report,indent=2))
if __name__=='__main__':main()
