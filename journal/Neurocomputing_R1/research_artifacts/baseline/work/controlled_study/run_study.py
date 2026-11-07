#!/usr/bin/env python3
"""Frozen, matched RBF experiment. The JSON protocol is the authority.

No original MATLAB files are edited. Run with --data-dir pointing to Code/.
All row indices in persisted NPZ files are zero-based in the original .mat data.
"""
import argparse
import csv
import hashlib
import json
import os
import platform
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import scipy
from scipy.io import loadmat
from scipy.linalg import svd
from scipy.spatial.distance import cdist, pdist
import sklearn
from sklearn.model_selection import train_test_split
from threadpoolctl import threadpool_info, threadpool_limits


def sha256(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def write_json(path, value):
    Path(path).write_text(json.dumps(value, indent=2, allow_nan=False) + '\n')


def write_csv(path, rows):
    if not rows:
        return
    keys = list(dict.fromkeys(k for row in rows for k in row))
    with Path(path).open('w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=keys)
        writer.writeheader()
        writer.writerows(rows)


def flatten(images, indices):
    # MATLAB reshape(...,784,n)' preserves the column order within each image.
    return images[:, :, indices].reshape(784, len(indices), order='F').T.astype(np.float64) / 255.0


def rls(H, Y, lam):
    """Samplewise RLS for ||HW-Y||_F^2 + lam ||W||_F^2."""
    P = np.eye(H.shape[1], dtype=np.float64) / lam
    W = np.zeros((H.shape[1], Y.shape[1]), dtype=np.float64)
    minimum_denom = float('inf')
    for h, y in zip(H, Y):
        ph = P @ h
        denom = 1.0 + h @ ph
        minimum_denom = min(minimum_denom, float(denom))
        gain = ph / denom
        W += np.outer(gain, y - h @ W)
        P -= np.outer(ph, ph) / denom
    return W, minimum_denom


def factor(H, Y):
    start = time.perf_counter()
    u, s, vt = svd(H, full_matrices=False, check_finite=False, lapack_driver='gesdd')
    uty = u.T @ Y
    return s, vt, uty, time.perf_counter() - start


def solve_from_factor(s, vt, uty, lam, n):
    start = time.perf_counter()
    if lam == 0:
        keep = s > max(n, len(s)) * np.finfo(np.float64).eps * s[0]
        filt = np.zeros_like(s)
        filt[keep] = 1.0 / s[keep]
    else:
        filt = s / (s * s + lam)
    W = vt.T @ (filt[:, None] * uty)
    return W, time.perf_counter() - start


def unit_tests():
    rng = np.random.default_rng(20261106)
    H = rng.normal(size=(80, 7))
    Y = rng.normal(size=(80, 3))
    checks = []
    for lam in [0.01, 0.1, 1.0, 2.0, 10.0, 100.0]:
        expected = np.linalg.solve(H.T @ H + lam * np.eye(7), H.T @ Y)
        actual, denom = rls(H, Y, lam)
        relative = np.linalg.norm(actual - expected) / np.linalg.norm(expected)
        assert actual.shape == (7, 3)
        assert relative < 1e-10, relative
        checks.append({'lambda': lam, 'relative_error': float(relative), 'minimum_denominator': denom})
    # Source images are uint8: float conversion must precede division.
    x = np.array([0, 1, 127, 255], dtype=np.uint8).astype(np.float64) / 255
    assert x.dtype == np.float64 and 0 < x[2] < 1 and x[3] == 1
    return {'synthetic_equivalence': checks, 'normalization': 'PASS', 'shape': 'PASS'}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--data-dir', type=Path, required=True)
    parser.add_argument('--output-dir', type=Path, default=Path(__file__).resolve().parent / 'results')
    args = parser.parse_args()
    here = Path(__file__).resolve().parent
    protocol = json.loads((here / 'protocol.json').read_text())
    expected_protocol_hash = (here / 'protocol.sha256').read_text().split()[0]
    assert sha256(here / 'protocol.json') == expected_protocol_hash
    source_hash = sha256(__file__)
    out = args.output_dir.resolve()
    out.mkdir(parents=True, exist_ok=True)
    if (out / 'COMPLETE.json').exists():
        raise RuntimeError('Completed results already exist; choose a new output directory for an intentional rerun.')
    with threadpool_limits(limits=1):
        checks = unit_tests()
        for name, expected in protocol['data'].items():
            assert sha256(args.data_dir / name) == expected, name
        checks['data_hashes'] = 'PASS'
        write_json(out / 'preflight_checks.json', checks)
        env = {'started_at_utc': datetime.now(timezone.utc).isoformat(), 'python': sys.version,
               'numpy': np.__version__, 'scipy': scipy.__version__, 'sklearn': sklearn.__version__,
               'platform': platform.platform(), 'processor': platform.processor(), 'cpu_count': os.cpu_count(),
               'threads': threadpool_info(), 'source_sha256': source_hash,
               'protocol_sha256': expected_protocol_hash, 'data_sha256': protocol['data']}
        write_json(out / 'environment.json', env)
        train = loadmat(args.data_dir / 'MNIST_train.mat')
        images, labels = train['imagestrain'], train['labelstrain'].ravel().astype(np.int64)
        test = loadmat(args.data_dir / 'MNIST_test.mat')
        test_ids = np.arange(protocol['test_n'])
        Xtest = flatten(test['images'], test_ids)
        ytest = test['labels'].ravel().astype(np.int64)
        validation_rows, test_rows, rls_rows, feature_rows, selected_rows = [], [], [], [], []
        eye = np.eye(10)
        for seed in protocol['seeds']:
            seedstart = time.perf_counter()
            train_ids, remainder = train_test_split(np.arange(len(labels)), train_size=protocol['train_n'],
                                                    stratify=labels, random_state=seed)
            val_ids, unused = train_test_split(remainder, train_size=protocol['validation_n'],
                                              stratify=labels[remainder], random_state=seed+1000)
            assert len(np.intersect1d(train_ids, val_ids)) == 0
            X, Xval = flatten(images, train_ids), flatten(images, val_ids)
            y, yval = labels[train_ids], labels[val_ids]
            Y = eye[y]
            center_rows = np.random.default_rng(seed).choice(len(X), size=protocol['centers_n'], replace=False)
            C = X[center_rows]
            center_ids = train_ids[center_rows]
            distance_scale = float(np.median(pdist(C)) / np.sqrt(2))
            widths = [('fixed_1', 1.0), ('scale_025', .25*distance_scale),
                      ('scale_05', .5*distance_scale), ('scale_1', distance_scale)]
            ts = time.perf_counter()
            Dtrain, Dval = cdist(X, C, metric='sqeuclidean'), cdist(Xval, C, metric='sqeuclidean')
            train_val_distance_seconds = time.perf_counter()-ts
            cache = {}
            winner = None
            winner_correct = -1
            for wi, (widthname, sigma) in enumerate(widths):
                ts = time.perf_counter()
                H, Hval = np.exp(-Dtrain/(2*sigma*sigma)), np.exp(-Dval/(2*sigma*sigma))
                exp_seconds = time.perf_counter()-ts
                s, vt, uty, factor_seconds = factor(H, Y)
                feature_rows.append({'seed':seed,'width':widthname,'sigma':sigma,'distance_scale':distance_scale,
                                     'train_val_distance_seconds_shared':train_val_distance_seconds,
                                     'train_val_exponential_seconds':exp_seconds,'factorization_seconds':factor_seconds,
                                     'train_activation_median':float(np.median(H)),
                                     'train_activation_fraction_below_1e_12':float(np.mean(H<1e-12)),
                                     'largest_singular_value':float(s[0]),'smallest_singular_value':float(s[-1]),
                                     'condition_number':float(s[0]/s[-1]),'dense_train_feature_bytes':H.nbytes})
                models = {}
                for li, lam in enumerate(protocol['lambda_grid_in_order']):
                    W, solve_seconds = solve_from_factor(s, vt, uty, lam, len(X))
                    pred = np.argmax(Hval @ W, axis=1)
                    correct = int(np.sum(pred==yval))
                    validation_rows.append({'seed':seed,'width':widthname,'sigma':sigma,'lambda':lam,
                                            'validation_correct':correct,'validation_n':len(yval),
                                            'validation_accuracy':correct/len(yval),'svd_seconds_shared':factor_seconds,
                                            'filter_solve_seconds':solve_seconds})
                    models[lam] = W
                    if correct>winner_correct:
                        winner_correct=correct
                        winner=(widthname,sigma,lam)
                cache[widthname]={'H':H,'models':models,'sigma':sigma,'svd_seconds':factor_seconds}
            assert winner is not None
            widthname,sigma,lam=winner
            selected_rows.append({'seed':seed,'width':widthname,'sigma':sigma,'lambda':lam,
                                  'validation_correct':winner_correct,'validation_n':len(yval)})
            # Persist the selection before computing any test scores.
            write_json(out / f'seed_{seed}_selection.json',selected_rows[-1])
            ts=time.perf_counter()
            Dtest=cdist(Xtest,C,metric='sqeuclidean')
            test_distance_seconds=time.perf_counter()-ts
            Htests={name:np.exp(-Dtest/(2*sig*sig)) for name,sig in widths}
            predictions={'test_ids':test_ids,'test_y':ytest,'train_ids':train_ids,'validation_ids':val_ids,
                         'center_ids':center_ids,'center_labels':labels[center_ids]}
            conditions=[('validation_selected',widthname,lam),('fixed_1_pinv','fixed_1',0.0),
                        ('fixed_1_lambda_1','fixed_1',1.0),('scale_1_pinv','scale_1',0.0),
                        ('scale_1_lambda_1','scale_1',1.0)]
            for condition,name,lamb in conditions:
                W=cache[name]['models'][lamb]
                scores=Htests[name] @ W
                pred=np.argmax(scores,axis=1)
                correct=int(np.sum(pred==ytest))
                predictions[condition]=pred
                predictions[condition+'_scores']=scores
                test_rows.append({'seed':seed,'condition':condition,'width':name,'sigma':cache[name]['sigma'],
                                  'lambda':lamb,'test_correct':correct,'test_errors':len(ytest)-correct,
                                  'test_n':len(ytest),'test_accuracy':correct/len(ytest),
                                  'test_distance_seconds_shared':test_distance_seconds})
            pred=labels[center_ids][np.argmin(Dtest,axis=1)]
            predictions['nearest_prototype']=pred
            correct=int(np.sum(pred==ytest))
            test_rows.append({'seed':seed,'condition':'nearest_prototype','width':'euclidean','sigma':'','lambda':'',
                              'test_correct':correct,'test_errors':len(ytest)-correct,'test_n':len(ytest),
                              'test_accuracy':correct/len(ytest),'test_distance_seconds_shared':test_distance_seconds})
            eq_conditions=[('fixed_1',v) for v in protocol['lambda_grid_in_order'] if v>0]
            chosen=(widthname,lam if lam>0 else 1.0)
            if chosen not in eq_conditions:
                eq_conditions.append(chosen)
            for name,lamb in eq_conditions:
                ts=time.perf_counter()
                Wr,minimum_denom=rls(cache[name]['H'],Y,lamb)
                seconds=time.perf_counter()-ts
                Wb=cache[name]['models'][lamb]
                sb,sr=Htests[name]@Wb,Htests[name]@Wr
                rel=float(np.linalg.norm(Wr-Wb)/max(np.linalg.norm(Wb),np.finfo(float).tiny))
                disagreements=int(np.sum(np.argmax(sb,axis=1)!=np.argmax(sr,axis=1)))
                rls_rows.append({'seed':seed,'width':name,'sigma':cache[name]['sigma'],'lambda':lamb,'alpha':1/lamb,
                                 'relative_weight_error':rel,'max_absolute_test_score_error':float(np.max(np.abs(sr-sb))),
                                 'test_prediction_disagreements':disagreements,'test_n':len(ytest),
                                 'minimum_update_denominator':minimum_denom,'rls_solver_seconds':seconds,
                                 'batch_svd_seconds':cache[name]['svd_seconds']})
            np.savez_compressed(out/f'seed_{seed}_predictions.npz',**predictions)
            write_csv(out/'validation_grid.csv',validation_rows)
            write_csv(out/'test_metrics.csv',test_rows)
            write_csv(out/'rls_equivalence.csv',rls_rows)
            write_csv(out/'feature_diagnostics.csv',feature_rows)
            write_csv(out/'selected_configurations.csv',selected_rows)
            print(json.dumps({'seed':seed,'selected_width':widthname,'sigma':sigma,'lambda':lam,
                              'selected_test_accuracy':[r['test_accuracy'] for r in test_rows if r['seed']==seed and r['condition']=='validation_selected'][0],
                              'elapsed_seconds':time.perf_counter()-seedstart}),flush=True)
        assert sha256(__file__)==source_hash
        assert sha256(here/'protocol.json')==expected_protocol_hash
        complete={'finished_at_utc':datetime.now(timezone.utc).isoformat(),'seeds_completed':len(protocol['seeds']),
                  'validation_models':len(validation_rows),'test_conditions':len(test_rows),'rls_checks':len(rls_rows),
                  'source_sha256':source_hash,'protocol_sha256':expected_protocol_hash,
                  'file_sha256':{p.name:sha256(p) for p in sorted(out.iterdir()) if p.is_file()}}
        write_json(out/'COMPLETE.json',complete)
        print('COMPLETE',flush=True)


if __name__=='__main__':
    main()
