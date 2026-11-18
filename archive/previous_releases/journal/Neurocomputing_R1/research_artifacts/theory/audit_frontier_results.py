"""Independent arithmetic/formula audit of supplementary frontier evidence.

Imports the frozen runner only to load declared input images. Certificate terms,
guards, endpoint choices, metrics, summary values and readout checks are rebuilt.
"""
import csv
import hashlib
import json
import sys
from pathlib import Path

import numpy as np
from scipy.spatial.distance import cdist
from threadpoolctl import threadpool_limits

ROOT = Path(__file__).resolve().parents[1]
EXP = ROOT / "baseline/work/v2/experiment"
OUT = ROOT / "frontier/results"
sys.path.insert(0, str(EXP))
import run_experiment as original_data_loader

def rows(path):
    return list(csv.DictReader(path.open()))

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def check_float(a, b):
    assert np.isclose(float(a), float(b), rtol=2e-12, atol=2e-12), (a, b)

def calculate_constants(H, labels, selected, floor):
    n, k = H.shape
    onehot = np.eye(10)[labels]
    yc = onehot[selected]
    E = H.copy()
    E[selected, np.arange(k)] = 0
    ec = E[selected]
    non = np.ones(n, bool)
    non[selected] = False
    V = ec @ yc
    P = E[non].T @ onehot[non]
    Q = E.T @ (E @ yc)
    beta = ec.sum(axis=1).max()
    gamma = max(1 - beta, 0) ** 2
    eta = np.sqrt(np.sum(E * E))
    den = gamma + floor
    value = np.full((3, 10, 10), np.inf)
    if den > 0:
        for a in range(10):
            for b in range(10):
                if a == b:
                    value[:, a, b] = 0
                    continue
                v, p, q = V[:, a] + V[:, b], P[:, a] + P[:, b], Q[:, a] + Q[:, b]
                value[0, a, b] = max(np.sqrt(np.sum(((abs(floor-1)*v+(floor+1)*p+q)/den)**2)), np.sqrt(np.sum((v+p)**2)))
                value[1, a, b] = np.sqrt(np.sum((((floor+1)*(v+p)+q)/den)**2))
                value[2, a, b] = ((floor+1)*eta*np.sqrt(onehot[:, [a,b]].sum())+eta**2*np.sqrt(yc[:, [a,b]].sum()))/den
    return value

result = {"groups": 0, "grid_coverage_rows_recomputed": 0, "endpoint_rows_recomputed": 0,
          "query_frontier_rows_recomputed": 0, "selected_width_training_terms_recomputed": 0,
          "selected_readouts_normal_equations_checked": 0, "stored_prediction_labels_reconstructed": 0,
          "manifest_files_verified": 0, "certified_endpoint_disagreements": 0,
          "maximum_normal_equation_relative_residual": 0.0,
          "maximum_selected_constant_relative_difference": 0.0}
coverage = {(r['dataset'],int(r['seed']),int(r['K']),int(r['grid_index']),int(r['lambda_floor']),r['method']):r for r in rows(OUT/'grid_coverage.csv')}
endpoints = {(r['dataset'],int(r['seed']),int(r['K']),int(r['lambda_floor']),r['target']):r for r in rows(OUT/'endpoint_metrics.csv')}
frontiers = {(r['dataset'],int(r['seed']),int(r['K']),int(r['lambda_floor']),r['method']):r for r in rows(OUT/'query_frontier_summary.csv')}
manifest = json.loads((OUT/'MANIFEST_SHA256.json').read_text())
for name, digest in manifest.items():
    assert sha(OUT/name) == digest, name
    result['manifest_files_verified'] += 1
freeze = json.loads((ROOT/'frontier/FREEZE.json').read_text())
assert sha(ROOT/'frontier/protocol.json') == freeze['protocol_sha256']
assert sha(ROOT/'frontier/run_frontier.py') == freeze['runner_sha256']
assert sha(EXP/'certificate.py') == freeze['certificate_sha256']
protocol = json.loads((EXP/'protocol.json').read_text())
guard = protocol['strict_guard']
tie_guard = protocol['nearest_tie_relative']
allfreeze = json.loads((OUT/'ALL_PREDICTIONS_FROZEN.json').read_text())
group_freezes = {(r['dataset'],r['seed'],r['K']):r['freeze_sha256'] for r in allfreeze['groups']}
with threadpool_limits(1):
    for dataset in protocol['datasets']:
        images, labels, query_images, ids = original_data_loader.data_load(dataset, protocol)
        Xq = original_data_loader.flatten(query_images)
        targets = np.load(EXP/'results'/f'{dataset}_evaluation_labels.npy')
        for seed in protocol['seeds']:
            for k in protocol['prototype_budgets']:
                group = OUT/f'{dataset}_seed{seed}_K{k}'
                receipt = json.loads((group/'PREDICTIONS_FROZEN.json').read_text())
                assert sha(group/'PREDICTIONS_FROZEN.json') == group_freezes[dataset,seed,k]
                for filename,digest in receipt['files'].items():
                    assert sha(group/filename) == digest
                assert receipt['frozen_utc'] <= allfreeze['frozen_utc']
                with np.load(group/'frontiers_before_labels.npz') as z:
                    X = original_data_loader.flatten(images[z['train_ids']])
                    y = labels[z['train_ids']]
                    centers = z['center_rows']
                    yc = y[centers]
                    D = cdist(Xq, X[centers], 'sqeuclidean')
                    Dt = cdist(X, X[centers], 'sqeuclidean')
                    ref = yc[np.argmin(D, axis=1)]
                    assert np.array_equal(ref,z['nearest_prototype'])
                    assert np.array_equal(ids,z['query_ids'])
                    masks=z['certificate_masks']; ratios=z['ratios']; widths=z['widths']; bounds=z['pair_constants']
                    assert len(ratios)==67
                    np.testing.assert_allclose(ratios,2.**np.linspace(-5,-2,67),rtol=1e-15,atol=0)
                    assert not np.any(masks[1:] & ~masks[:-1])
                    assert not np.any(masks[:,:,1] & ~masks[:,:,0])
                    assert not np.any(masks[:,:,2] & ~masks[:,:,1])
                    last=np.max(np.where(masks,np.arange(67)[:,None,None,None],-1),axis=0)
                    assert np.array_equal(last,z['last_certified_grid_index'])
                    assert np.array_equal(np.where(last<66,last+1,-1),z['next_failed_grid_index'])
                    assert np.array_equal(last<0,z['left_censored'])
                    assert np.array_equal(last==66,z['right_censored'])
                    smallest=np.sort(D,axis=1)[:,:2]
                    unique=(smallest[:,1]-smallest[:,0]) > tie_guard*np.maximum(1,smallest[:,1])
                    for wi,t in enumerate(widths):
                        response=np.exp(-(D-D.min(axis=1,keepdims=True))/(2*t*t))
                        mass=response@np.eye(10)[yc]
                        norm=np.sqrt((response**2).sum(axis=1))
                        lhs=1-mass
                        for li,lo in enumerate(z['lambda_floors']):
                            for mi,method in enumerate(z['methods']):
                                rhs=norm[:,None]*bounds[wi,li,mi,ref,:]
                                accepted=(lhs-rhs)>guard*(1+np.abs(lhs)+np.abs(rhs))
                                accepted[np.arange(len(ref)),ref]=True
                                check=unique & accepted.all(axis=1)
                                assert np.array_equal(check,masks[wi,li,mi])
                                record=coverage[dataset,seed,k,wi,int(lo),str(method)]
                                assert int(record['certified'])==int(check.sum())
                                check_float(record['coverage'],check.mean())
                                check_float(record['sigma'],t)
                                result['grid_coverage_rows_recomputed']+=1
                    for li,lo in enumerate(z['lambda_floors']):
                        for mi,method in enumerate(z['methods']):
                            record=frontiers[dataset,seed,k,int(lo),str(method)]
                            indices=last[li,mi]; vals=ratios[indices[indices>=0]]
                            assert int(record['left_censored'])==int((indices<0).sum())
                            assert int(record['right_censored'])==int((indices==66).sum())
                            if len(vals):
                                for field,value in [('minimum_last_certified_ratio',vals.min()),('q10_last_certified_ratio',np.quantile(vals,.1)),('median_last_certified_ratio',np.median(vals)),('q90_last_certified_ratio',np.quantile(vals,.9)),('maximum_last_certified_ratio',vals.max())]:
                                    check_float(record[field],value)
                            else:
                                assert all(record[field]=='' for field in ['minimum_last_certified_ratio','q10_last_certified_ratio','median_last_certified_ratio','q90_last_certified_ratio','maximum_last_certified_ratio'])
                            result['query_frontier_rows_recomputed']+=1
                    with np.load(EXP/'results'/group.name/'predictions_before_labels.npz') as old:
                        assert np.array_equal(masks[[22,44,66]],old['certificate_masks'][[1,2,3]])
                        for li,lo in enumerate(z['lambda_floors']):
                            counts=masks[:,li,0].sum(axis=1)
                            for target, threshold in [('any',1),('50pct',int(np.ceil(len(ref)/2))),('90pct',int(np.ceil(.9*len(ref))))]:
                                chosen=np.flatnonzero(counts>=threshold)[-1]
                                record=endpoints[dataset,seed,k,int(lo),target]
                                assert int(record['grid_index'])==chosen and record['available']=='True'
                                fi=int(np.flatnonzero(z['fit_grid_indices']==chosen)[0]);pred=z['predictions'][fi,li];mask=masks[chosen,li,0]
                                oldli=int(np.flatnonzero(old['probe_penalties']==lo)[0]);oldacc=(old['predictions'][:,oldli]==targets).mean(axis=1);best=int(np.argmax(oldacc))
                                metrics={'coverage':mask.mean(),'accuracy':np.mean(pred==targets),'nearest_accuracy':np.mean(ref==targets),'nearest_agreement':np.mean(pred==ref),'certified_accuracy':np.mean(pred[mask]==targets[mask]),'best_frozen_sampled_accuracy':oldacc[best],'best_frozen_sampled_sigma':old['probe_widths'][best],'accuracy_loss_vs_best_frozen_pp':100*(oldacc[best]-np.mean(pred==targets))}
                                for field,value in metrics.items():check_float(record[field],value)
                                result['certified_endpoint_disagreements']+=int(np.sum(mask&(pred!=ref)))
                                assert old['probe_widths'][best]>widths[chosen]
                                result['endpoint_rows_recomputed']+=1
                    for fi,wi in enumerate(z['fit_grid_indices']):
                        H=np.exp(-Dt/(2*widths[wi]**2));H[centers,np.arange(k)]=1
                        Gram=H.T@H;cross=H.T@np.eye(10)[y]
                        response=np.exp(-(D-D.min(axis=1,keepdims=True))/(2*widths[wi]**2))
                        for li,lo in enumerate(z['lambda_floors']):
                            fresh=calculate_constants(H,y,centers,int(lo));saved=bounds[wi,li]
                            np.testing.assert_allclose(fresh,saved,rtol=2e-12,atol=2e-12)
                            finite=np.isfinite(fresh)&np.isfinite(saved)
                            rel=np.max(np.abs(fresh[finite]-saved[finite])/(1+np.abs(saved[finite])))
                            result['maximum_selected_constant_relative_difference']=max(result['maximum_selected_constant_relative_difference'],float(rel))
                            W=z['weights'][fi,li]
                            residual=np.linalg.norm((Gram+lo*np.eye(k))@W-cross)/(1+np.linalg.norm(cross))
                            assert residual<1e-9,residual
                            result['maximum_normal_equation_relative_residual']=max(result['maximum_normal_equation_relative_residual'],float(residual))
                            assert np.array_equal(np.argmax(response@W,axis=1),z['predictions'][fi,li])
                            result['stored_prediction_labels_reconstructed']+=len(ref)
                            result['selected_readouts_normal_equations_checked']+=1
                        result['selected_width_training_terms_recomputed']+=1
                result['groups']+=1
result['status']='PASS'
result['all_selected_best_frozen_widths_broader']=True
(Path(__file__).parent/'frontier_independent_audit.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps(result,indent=2))
