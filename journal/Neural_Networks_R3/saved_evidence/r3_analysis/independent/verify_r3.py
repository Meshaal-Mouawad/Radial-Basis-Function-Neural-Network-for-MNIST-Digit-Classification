#!/usr/bin/env python3
"""Independent R3 audit: reconstruct core results from R2 images and weights.

No analysis-runner imports, no model fitting, and no mutation of source evidence.
Run with evidence/ and r3_analysis/ beside one another.
"""
import csv
import gzip
import hashlib
import json
import time
from pathlib import Path

import numpy as np
from scipy.io import loadmat
from scipy.spatial.distance import cdist
from threadpoolctl import threadpool_limits

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
EVID = ROOT / 'evidence'
BASE = EVID / 'baseline/evidence/baseline'
EXP = BASE / 'work/v2/experiment/results'
DIAG = EVID / 'new_analysis/limit_diagnostic'
FRONT = EVID / 'baseline/evidence/frontier/results'
M3 = ROOT / 'r3_analysis/m3/results'
M12 = ROOT / 'r3_analysis/m1_m2/results'


def readcsv(path):
    with path.open() as f:
        return list(csv.DictReader(f))


def imgs(path):
    raw = gzip.decompress(path.read_bytes())
    shape = np.frombuffer(raw[:16], dtype='>u4')
    assert shape[0] == 2051
    return np.frombuffer(raw[16:], dtype=np.uint8).reshape(tuple(shape[1:]))


def labels(path):
    raw = gzip.decompress(path.read_bytes())
    assert int.from_bytes(raw[:4], 'big') == 2049
    return np.frombuffer(raw[8:], dtype=np.uint8).astype(int)


def vectors(images):
    return np.stack([x.ravel(order='F') for x in images]).astype(np.float64) / 255


def selected(score, m, ids, eligible):
    indices = np.flatnonzero(eligible)
    order = np.lexsort((indices, ids[indices], -score[indices]))
    mask = np.zeros(len(score), dtype=bool)
    mask[indices[order[:m]]] = True
    assert mask.sum() == m
    return mask


def witness(scores, nearest):
    reference = scores[np.arange(len(nearest)), nearest]
    differences = scores - reference[:, None]
    guards = 1e-10 * (1 + np.abs(scores) + np.abs(reference[:, None]))
    differences[np.arange(len(nearest)), nearest] = -np.inf
    return np.any(differences > guards, axis=1)


def main():
    started = time.perf_counter()
    counts = dict(groups=0, m3_prediction_labels=0, m3_selector_masks=0,
                  m3_per_seed_rows=0, m3_class_count_rows=0,
                  m1_validation_prediction_labels=0, m1_threshold_query_widths=0,
                  m1_finite_reversal_checks=0, m2_region_unions=0)
    max_threshold_relative_error = 0.0
    m3rows = readcsv(M3 / 'per_seed.csv')
    m3classes = readcsv(M3 / 'class_counts.csv')
    m1rows = readcsv(M12 / 'm1_thresholds_per_seed.csv')
    m2rows = readcsv(M12 / 'm2_overlap_per_seed.csv')
    r2rectangles = readcsv(DIAG / 'original7_guarded/rectangles.csv')
    group_summary = []
    for dataset in ['mnist', 'fashion_mnist']:
        if dataset == 'mnist':
            mat = loadmat(BASE / 'repository/Code/MNIST_train.mat')
            images = mat['imagestrain'].transpose(2, 0, 1)
            ytrain = mat['labelstrain'].ravel().astype(int)
            qids0 = np.load(BASE / 'work/v2/design/reserved_training_ids.npy')
            qimages = images[qids0]
            truth = ytrain[qids0]
        else:
            folder = BASE / 'work/v2/data/fashion_mnist'
            images = imgs(folder / 'train-images-idx3-ubyte.gz')
            qimages = imgs(folder / 't10k-images-idx3-ubyte.gz')
            ytrain = labels(folder / 'train-labels-idx1-ubyte.gz')
            truth = labels(folder / 't10k-labels-idx1-ubyte.gz')
        assert np.array_equal(truth, np.load(EXP / f'{dataset}_evaluation_labels.npy'))
        Q = vectors(qimages)
        for seed in [11, 22, 33, 44, 55]:
            name = f'{dataset}_seed{seed}_K100'
            old = np.load(EXP / name / 'predictions_before_labels.npz')
            local = np.load(DIAG / 'local_tail' / f'{name}.npz')
            fitted = np.load(DIAG / 'local_tail_validation' / f'{name}.npz')
            saved3 = np.load(M3 / f'{name}.npz')
            saved12 = np.load(M12 / f'{name}.npz')
            C = vectors(images[old['center_ids']])
            D = cdist(Q, C, 'sqeuclidean')
            nearest = old['center_labels'][np.argmin(D, axis=1)]
            assert np.array_equal(nearest, old['nearest_prototype'])
            deltaD = D - D.min(axis=1, keepdims=True)
            n = len(truth)
            scale = old['width_upper_bounds'][1] * 16
            qids = old['query_ids']
            assert np.array_equal(saved3['truth'], truth)
            assert np.array_equal(saved3['query_ids'], qids)
            dmargin = np.min(np.where(old['center_labels'][None, :] != nearest[:, None], D, np.inf), axis=1) - D.min(axis=1)
            assert np.allclose(dmargin, saved3['prototype_distance_margin'], rtol=0, atol=1e-12)
            cert_rows = []
            for ri, ratio in enumerate([.5, 1.]):
                t = ratio * scale
                A = local[f'case{2 * ri}_A_t']
                op = np.linalg.norm(A, ord=2)
                W = fitted[f't{ri}_weights'][0, 2]
                scores = np.exp(-D / (2 * t*t)) @ W
                normal = np.exp(-deltaD / (2 * t*t)) @ W
                pred = scores.argmax(axis=1)
                assert np.array_equal(pred, fitted[f't{ri}_predictions'][0, 2])
                assert np.array_equal(pred, saved3[f't{ri}_predictions'])
                assert np.array_equal(pred, normal.argmax(axis=1))
                assert np.allclose(scores, saved3[f't{ri}_raw_scores'], rtol=1e-12, atol=1e-14)
                assert np.allclose(normal, saved3[f't{ri}_normalized_scores'], rtol=1e-12, atol=1e-14)
                sort = np.sort(scores, axis=1)
                margin = sort[:, -1] - sort[:, -2]
                sn = np.sort(normal, axis=1)
                normmargin = sn[:, -1] - sn[:, -2]
                cert = local[f'case{2 * ri}_threshold'] <= 10*op
                m = int(cert.sum())
                agree = pred == nearest
                assert np.all(agree[cert])
                allrows = np.ones(n, bool)
                masks = {'full_query': allrows, 'certificate': cert,
                         'score_margin': selected(margin, m, qids, allrows),
                         'normalized_score_margin': selected(normmargin, m, qids, allrows),
                         'prototype_distance_margin': selected(dmargin, m, qids, allrows),
                         'agreement_gated_score_margin': selected(margin, m, qids, agree),
                         'agreement_gated_distance_margin': selected(dmargin, m, qids, agree)}
                for selector, mask in masks.items():
                    if selector != 'full_query':
                        assert mask.sum() == m
                        assert np.array_equal(mask, saved3[f't{ri}_{selector}_mask'])
                        counts['m3_selector_masks'] += 1
                    rr = [x for x in m3rows if x['dataset'] == dataset and int(x['seed']) == seed and float(x['t_over_sC']) == ratio and x['selector'] == selector]
                    assert len(rr) == 1
                    rr = rr[0]
                    acc = 100*np.mean(pred[mask] == truth[mask])
                    assert int(rr['selected']) == mask.sum()
                    assert abs(float(rr['accuracy_pct']) - acc) < 1e-11
                    assert abs(float(rr['query_majority_reference_pct']) - 100*np.bincount(truth).max()/n) < 1e-11
                    pc = np.bincount(pred[mask], minlength=10)
                    tc = np.bincount(truth[mask], minlength=10)
                    for cl in range(10):
                        cr = [x for x in m3classes if x['dataset'] == dataset and int(x['seed']) == seed and float(x['t_over_sC']) == ratio and x['selector'] == selector and int(x['class_label']) == cl]
                        assert len(cr) == 1
                        assert int(cr[0]['predicted_count']) == pc[cl]
                        assert int(cr[0]['true_count']) == tc[cl]
                        counts['m3_class_count_rows'] += 1
                    counts['m3_per_seed_rows'] += 1
                if dataset == 'mnist' and ratio == 1:
                    assert np.all(pred == 1)
                counts['m3_prediction_labels'] += n
                cert_rows.append(dict(width=ratio, certificate=int(m),
                                      accuracy=float(np.mean(pred[cert] == truth[cert])*100)))
            # Independent validation scoring of the complete 16 x 6 archived grid.
            valid = old['validation_ids']
            assert not np.intersect1d(valid, old['train_ids']).size
            if dataset == 'mnist':
                assert not np.intersect1d(valid, qids).size
            V = vectors(images[valid])
            DV = cdist(V, C, 'sqeuclidean')
            DV -= DV.min(axis=1, keepdims=True)
            valpred = np.empty_like(saved12['validation_predictions'])
            valacc = np.zeros_like(saved12['validation_accuracy'])
            original_records = []
            for wi, w in enumerate(old['probe_widths']):
                vfeat = np.exp(-DV/(2*w*w))
                qfeat = np.exp(-deltaD/(2*w*w))
                for li, penalty in enumerate(old['probe_penalties']):
                    W = old['weights'][wi, li]
                    valpred[wi, li] = (vfeat @ W).argmax(axis=1)
                    valacc[wi, li] = np.mean(valpred[wi, li] == ytrain[valid])
                    mask = witness(qfeat @ W, nearest)
                    if penalty == 0 and old['numerical_ranks'][wi] < 100:
                        mask[:] = False
                    original_records.append((w, penalty, mask))
            assert np.array_equal(valpred, saved12['validation_predictions'])
            assert np.array_equal(valacc, saved12['validation_accuracy'])
            competitive = valacc >= .95*valacc.max()
            counts['m1_validation_prediction_labels'] += valpred.size
            # Independently reconstruct both finite-witness banks.
            extended_records = list(original_records)
            frontier = np.load(FRONT / name / 'frontiers_before_labels.npz')
            for wi, w in enumerate(frontier['widths'][frontier['fit_grid_indices']]):
                qfeat = np.exp(-deltaD/(2*w*w))
                for li, penalty in enumerate(frontier['lambda_floors']):
                    mask = witness(qfeat @ frontier['weights'][wi, li], nearest)
                    if penalty == 0 and frontier['numerical_ranks'][wi] < 100:
                        mask[:] = False
                    extended_records.append((w, penalty, mask))
            for ri, ratio in enumerate([.5, 1.]):
                op = np.linalg.norm(local[f'case{2*ri}_A_t'], ord=2)
                for li, mult in enumerate([10, 100]):
                    for si, fraction in enumerate([.95, .99, 1.]):
                        w = scale*ratio*fraction
                        mask = witness(np.exp(-deltaD/(2*w*w)) @ fitted[f't{ri}_weights'][li, si], nearest)
                        extended_records.append((w, mult*op, mask))
            old_limit = np.load(DIAG / 'original7_guarded' / f'{name}.npz')
            dense = np.load(DIAG / 'dense67_guarded' / f'{name}.npz')
            X = vectors(images[old['train_ids']])
            DT = cdist(X, C, 'sqeuclidean')
            y = ytrain[old['train_ids']]
            for wi, w in enumerate(old['width_upper_bounds']):
                H = np.exp(-DT/(2*w*w))
                A = H.T @ H
                Z = np.stack([H[y == c].sum(axis=0) for c in range(10)], axis=1)
                op = np.linalg.norm(A, ord=2)
                r = np.exp(-deltaD/(2*w*w))
                scores = r @ Z
                candidates = np.full((n, 10), np.inf)
                for a in range(10):
                    ii = np.flatnonzero(nearest == a)
                    for b in range(10):
                        if a == b:
                            continue
                        gap = scores[ii, b] - scores[ii, a]
                        eligible = gap > 1e-10*(1 + abs(scores[ii, b]) + abs(scores[ii, a]))
                        jj = ii[eligible]
                        candidates[jj, b] = np.linalg.norm(r[jj], axis=1)*np.linalg.norm(A @ (Z[:, b] - Z[:, a]))/gap[eligible]
                th = np.min(candidates, axis=1)
                finite = np.isfinite(th)
                assert np.array_equal(finite, np.isfinite(saved12['threshold'][wi]))
                assert np.allclose(th[finite], saved12['threshold'][wi, finite], rtol=1e-9, atol=1e-10)
                max_threshold_relative_error = max(max_threshold_relative_error, float(np.max(abs(th[finite]/saved12['threshold'][wi, finite] - 1))) if finite.any() else 0.)
                assert np.allclose(th[finite]/op, saved12['normalized_threshold'][wi, finite], rtol=1e-9, atol=1e-10)
                idx = np.flatnonzero(np.isclose(old['probe_widths'], w, rtol=1e-13, atol=0))
                assert len(idx) == 1
                pcomp = old['probe_penalties'][competitive[idx[0]]]
                cm = np.max(pcomp) if len(pcomp) else np.nan
                assert (np.isnan(cm) and np.isnan(saved12['competitive_max_same_width'][wi])) or cm == saved12['competitive_max_same_width'][wi]
                mr = [x for x in m1rows if x['dataset'] == dataset and int(x['seed']) == seed and int(x['width_index']) == wi][0]
                assert int(mr['strict_limit_queries']) == finite.sum()
                if np.isfinite(cm):
                    assert int(mr['bound_within_same_width_competitive']) == np.sum(th < cm)
                counts['m1_threshold_query_widths'] += n
                # Every finite sufficient bound is tested through a separate spectral solve.
                ev, U = np.linalg.eigh(A)
                cc = np.argmin(candidates[finite], axis=1)
                pair = (U.T @ (Z[:, cc] - Z[:, nearest[finite]])).T
                lam = th[finite]*1.001
                scaled_margin = np.sum((r[finite] @ U)*pair/(1 + ev[None, :]/lam[:, None]), axis=1)
                assert np.all(scaled_margin > 0)
                counts['m1_finite_reversal_checks'] += len(lam)
                limit = np.any(old_limit['endpoint_obstruction'][old_limit['widths'] <= w*(1+1e-14)], axis=0)
                limit |= np.any(dense['endpoint_obstruction'][dense['widths'] <= w*(1+1e-14)], axis=0)
                assert np.array_equal(limit, saved12['dense_limit_prefix'][wi])
                for li, floor in enumerate(old['lambda_lower_bounds']):
                    f0 = np.any([mask for ww, ll, mask in original_records if ww <= w*(1+1e-14) and ll >= floor], axis=0)
                    f1 = np.any([mask for ww, ll, mask in extended_records if ww <= w*(1+1e-14) and ll >= floor], axis=0)
                    assert np.array_equal(f0, saved12['finite_original'][wi, li])
                    assert np.array_equal(f1, saved12['finite_all_archived'][wi, li])
                    assert not np.any(saved12['certified'][wi, li] & (limit | f1))
                    rr = [x for x in m2rows if x['dataset'] == dataset and int(x['seed']) == seed and int(x['width_index']) == wi and int(x['penalty_floor']) == floor][0]
                    r2lim = old_limit['prefix_obstruction'][wi]
                    original_union = r2lim | f0
                    frozen_row = [x for x in r2rectangles if x['dataset'] == dataset and int(x['seed']) == seed and int(x['width_index']) == wi and float(x['lambda_floor']) == floor][0]
                    assert int(frozen_row['combined_excluded']) == original_union.sum()
                    assert int(rr['r2_union']) == original_union.sum()
                    assert int(rr['r2_limit_only_vs_all']) == (r2lim & ~f1).sum()
                    for key, mask in [('limit_only_vs_original', limit & ~f0), ('limit_only_vs_all', limit & ~f1), ('all_finite_only_vs_limit', f1 & ~limit), ('combined_full', limit | f1), ('expanded_finite_unique', f1 & ~f0)]:
                        assert int(rr[key]) == mask.sum()
                    counts['m2_region_unions'] += 1
            counts['groups'] += 1
            group_summary.append(dict(group=name, m3=cert_rows, validation_best_accuracy_pct=float(valacc.max()*100)))
            print(name, 'PASS', flush=True)
    # Verify independently aggregated equal-seed summaries, not only row values.
    for row in readcsv(M3 / 'summary.csv'):
        rr = [x for x in m3rows if x['dataset'] == row['dataset'] and x['t_over_sC'] == row['t_over_sC'] and x['selector'] == row['selector']]
        assert len(rr) == 5
        for metric in ['coverage_pct', 'accuracy_pct', 'certificate_minus_selector_pp']:
            v = np.array([float(x[metric]) for x in rr])
            assert abs(float(row[metric+'_mean'])-v.mean()) < 1e-10
            assert abs(float(row[metric+'_sd'])-v.std(ddof=1)) < 1e-10
    report = dict(status='PASS', method='Independent reconstruction from preserved R2 image data and archived weights; no runner imports and no new fits', counts=counts,
                  maximum_threshold_relative_error=max_threshold_relative_error,
                  all_certified_selector_labels_agree=True, all_equal_size_masks_match=True,
                  all_m1_m2_masks_match=True, normalized_and_raw_scores_preserve_labels=True,
                  mnist_full_query_predictions_at_t_sC_all_class_one=True,
                  random_reference='Exact finite-population expectation; full-query correctness independently reconstructed',
                  elapsed_seconds=time.perf_counter()-started, groups=group_summary,
                  script_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest())
    (HERE/'verification.json').write_text(json.dumps(report, indent=2)+'\n')
    print(json.dumps({k:v for k,v in report.items() if k != 'groups'}, indent=2))


if __name__ == '__main__':
    with threadpool_limits(1):
        main()
