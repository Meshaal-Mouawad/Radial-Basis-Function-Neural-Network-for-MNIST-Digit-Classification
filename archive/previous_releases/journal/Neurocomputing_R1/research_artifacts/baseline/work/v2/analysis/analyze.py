#!/usr/bin/env python3
"""Read-only descriptive analysis of the frozen prospective experiment.

Run from any working directory. No model fitting, threshold selection, or writes
to experiment/results occur. The result manifest and frozen source are verified
before analysis. Counts represent repeated query/condition evaluations.
"""
from pathlib import Path
import hashlib
import json
import sys
from datetime import datetime, timezone

import numpy as np
import pandas as pd
from scipy.io import loadmat
from scipy.spatial.distance import cdist
from threadpoolctl import threadpool_limits

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
EXP = ROOT / 'work/v2/experiment'
R = EXP / 'results'
FIG = HERE / 'figures'
sys.path.insert(0, str(EXP))
from run_experiment import idx_images, flatten
from certificate import query_features, METHODS

DATASETS = ['mnist', 'fashion_mnist']
DATASET_NAMES = {'mnist': 'MNIST', 'fashion_mnist': 'Fashion-MNIST'}
WIDTH_NAMES = ['absolute_1', 'scaled_1_16', 'scaled_1_8', 'scaled_1_4', 'scaled_1_2', 'scaled_1', 'scaled_2']
MULTIPLIERS = [None, .0625, .125, .25, .5, 1., 2.]
FLOORS = [0, 1, 100]
KEYS = ['dataset', 'K', 'width_index', 'lambda_lower']
CELL_KEYS = ['dataset', 'seed', 'K', 'width_index', 'lambda_lower']
METRICS = ['readout_correct', 'nearest_correct', 'vote_correct',
           'nearest_readout_agree', 'vote_readout_agree',
           'nearest_wrong_readout_right', 'nearest_right_readout_wrong']


def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def dump(name, value):
    (HERE / name).write_text(json.dumps(value, indent=2, allow_nan=False) + '\n')


def add_widths(frame):
    frame = frame.copy()
    frame['width_definition'] = frame.width_index.map(dict(enumerate(WIDTH_NAMES)))
    frame['width_multiplier'] = frame.width_index.map(dict(enumerate(MULTIPLIERS)))
    return frame


def record_summary(values):
    values = np.asarray(values, dtype=float)
    return {'mean': float(values.mean()), 'sample_sd': float(values.std(ddof=1)),
            'minimum': float(values.min()), 'maximum': float(values.max())}


def main():
    assert (R / 'COMPLETE.json').exists(), 'Wait for completed experiment.'
    complete = json.loads((R / 'COMPLETE.json').read_text())
    protocol = json.loads((EXP / 'protocol.json').read_text())
    manifest = json.loads((R / 'MANIFEST_SHA256.json').read_text())
    for name, digest in manifest.items():
        assert sha(R / name) == digest, name
    freeze = complete['source_hashes']
    assert sha(EXP / 'protocol.json') == freeze['protocol_sha256']
    assert sha(EXP / 'certificate.py') == freeze['certificate_source_sha256']
    assert sha(EXP / 'run_experiment.py') == freeze['run_source_sha256']
    FIG.mkdir(exist_ok=True)

    cert = add_widths(pd.read_csv(R / 'certificate_metrics_before_labels.csv'))
    end = add_widths(pd.read_csv(R / 'endpoint_accuracy_and_fidelity.csv'))
    correct = add_widths(pd.read_csv(R / 'certificate_accuracy.csv'))
    diagnostics = add_widths(pd.read_csv(R / 'feature_diagnostics.csv'))
    assert len(cert) == 1890 and len(end) == 630
    assert set(cert.method) == set(METHODS)
    assert cert.groupby(KEYS + ['method']).size().eq(5).all()
    assert cert.groupby(CELL_KEYS).size().eq(3).all()
    assert not cert.duplicated(CELL_KEYS + ['method']).any()
    assert not end.duplicated(CELL_KEYS).any()
    assert np.array_equal(cert.coverage.to_numpy(), (cert.certified / cert.n).to_numpy()) or np.allclose(cert.coverage, cert.certified / cert.n, atol=1e-15)
    assert not cert.certified_probe_violations.any()
    assert cert.probe_pairs.eq(9).all()
    assert cert.loc[cert.width_index != 1, 'certified'].eq(0).all()
    cert['coverage_percent'] = 100 * cert.certified / cert.n
    for metric in METRICS:
        end[metric + '_percent'] = 100 * end[metric] / end.n
    correct['certified_accuracy_percent'] = np.where(correct.certified > 0,
        100 * correct.certified_correct / correct.certified, np.nan)
    correct['coverage_percent'] = 100 * correct.certified / correct.n
    correct['fraction_of_agreements_certified_percent'] = np.where(correct.actual_agreements > 0,
        100 * correct.certified_among_agreements / correct.actual_agreements, np.nan)

    rows = []
    for keys, cell in cert.groupby(KEYS + ['method'], sort=True):
        values = cell.coverage_percent.to_numpy()
        rows.append(dict(zip(KEYS + ['method'], keys), seed_count=len(cell),
                         query_n_per_seed=int(cell.n.iloc[0]),
                         coverage_mean_percent=float(values.mean()),
                         coverage_sample_sd_pp=float(values.std(ddof=1)),
                         coverage_min_percent=float(values.min()),
                         coverage_max_percent=float(values.max()),
                         zero_coverage_seeds=int(cell.certified.eq(0).sum()),
                         applicable_seeds=int(cell.applicable.sum()),
                         certified_query_rectangles=int(cell.certified.sum()),
                         evaluated_query_rectangles=int(cell.n.sum()),
                         sigma_upper_min=float(cell.sigma_upper.min()),
                         sigma_upper_max=float(cell.sigma_upper.max())))
    cov = add_widths(pd.DataFrame(rows))
    rows = []
    for keys, cell in end.groupby(KEYS, sort=True):
        out = dict(zip(KEYS, keys), seed_count=len(cell), query_n_per_seed=int(cell.n.iloc[0]))
        for metric in METRICS:
            values = cell[metric + '_percent'].to_numpy()
            out[metric + '_mean_percent'] = float(values.mean())
            out[metric + '_sample_sd_pp'] = float(values.std(ddof=1))
            out[metric + '_total_count'] = int(cell[metric].sum())
        rows.append(out)
    ends = add_widths(pd.DataFrame(rows))
    pair = cert.pivot(index=CELL_KEYS, columns='method', values='coverage_percent').reset_index()
    pair['sharp_minus_basic_pp'] = pair.sharp - pair.basic
    pair['sharp_minus_frobenius_pp'] = pair.sharp - pair.cancellation_frobenius
    assert np.all(pair.sharp_minus_basic_pp == 0)
    assert np.all(pair.sharp_minus_frobenius_pp >= 0)

    # Tables retain every predeclared condition, including all zero outcomes.
    cert.to_csv(HERE / 'appendix_certificate_all_grid.csv', index=False)
    end.to_csv(HERE / 'appendix_endpoint_all_grid.csv', index=False)
    correct.to_csv(HERE / 'appendix_certificate_accuracy_all_grid.csv', index=False)
    cov.to_csv(HERE / 'appendix_coverage_summary.csv', index=False)
    ends.to_csv(HERE / 'appendix_endpoint_summary.csv', index=False)
    add_widths(pair).to_csv(HERE / 'appendix_paired_coverage_gains.csv', index=False)
    diagnostics.to_csv(HERE / 'appendix_feature_diagnostics.csv', index=False)

    main_rows = []
    for _, ep in ends.loc[ends.width_index.isin([0, 1])].iterrows():
        keys = {k: ep[k] for k in KEYS}
        rec = dict(keys, width_definition=ep.width_definition,
                   query_n_per_seed=int(ep.query_n_per_seed), seed_count=5)
        selected = cov.loc[(cov[KEYS] == pd.Series(keys)).all(axis=1)]
        for _, cv in selected.iterrows():
            for col in ['coverage_mean_percent', 'coverage_sample_sd_pp', 'zero_coverage_seeds',
                        'certified_query_rectangles', 'evaluated_query_rectangles']:
                rec[cv.method + '_' + col] = cv[col]
        for metric in ['readout_correct', 'nearest_correct', 'nearest_readout_agree']:
            rec[metric + '_mean_percent'] = ep[metric + '_mean_percent']
            rec[metric + '_sample_sd_pp'] = ep[metric + '_sample_sd_pp']
        main_rows.append(rec)
    pd.DataFrame(main_rows).to_csv(HERE / 'main_results.csv', index=False)

    # Reconstruction audits saved masks and margins only; no fitted readout is
    # changed or re-estimated. Only the images needed for query features are read.
    numeric = []
    groups = []
    all_masks_equal = True
    all_masks_nested = True
    method_dedup_counts = {method: 0 for method in METHODS}
    all_method_union_comparisons = 0
    all_method_union_violations = 0
    min_margin_cell = None
    min_ratio_cell = None
    with threadpool_limits(1):
        for dataset in DATASETS:
            if dataset == 'mnist':
                images = loadmat(ROOT / 'repository/Code/MNIST_train.mat', variable_names=['imagestrain'])['imagestrain'].transpose(2, 0, 1)
                queries = images[np.load(ROOT / 'work/v2/design/reserved_training_ids.npy')]
            else:
                images = idx_images(ROOT / 'work/v2/data/fashion_mnist/train-images-idx3-ubyte.gz')
                queries = idx_images(ROOT / 'work/v2/data/fashion_mnist/t10k-images-idx3-ubyte.gz')
            Xq = flatten(queries)
            for directory in sorted(R.glob(dataset + '_seed*_K*')):
                with np.load(directory / 'predictions_before_labels.npz') as z:
                    K, seed = int(z['K']), int(z['seed'])
                    D = cdist(Xq, flatten(images[z['center_ids']]), 'sqeuclidean')
                    yc = z['center_labels']; Yc = np.eye(10)[yc]
                    nn = z['nearest_prototype']; ws = z['width_upper_bounds']
                    lows = z['lambda_lower_bounds']; masks = z['certificate_masks']
                    bounds = z['pair_constants']; ranks = z['numerical_ranks']
                    saved_gaps = z['certificate_min_gaps']
                    predictions = z['predictions']; probe_widths = z['probe_widths']
                    penalties = z['probe_penalties']
                    assert len(nn) == len(Xq)
                    assert np.array_equal(nn, yc[np.argmin(D, axis=1)])
                    equal = np.array_equal(masks[:, :, 0], masks[:, :, 1])
                    nested = bool(np.all(~masks[:, :, 2] | masks[:, :, 1]) and np.all(~masks[:, :, 1] | masks[:, :, 0]))
                    all_masks_equal &= equal; all_masks_nested &= nested
                    assert equal and nested
                    nearest_two = np.partition(D, 1, axis=1)[:, :2]
                    distance_gap = nearest_two[:, 1] - nearest_two[:, 0]
                    tie_guard = protocol['nearest_tie_relative'] * np.maximum(1, np.max(nearest_two, axis=1))
                    near_ties = int(np.sum(distance_gap <= tie_guard))
                    tested = np.zeros((3,) + predictions.shape, dtype=bool)
                    local_cert_rows = cert[(cert.dataset == dataset) & (cert.seed == seed) & (cert.K == K)]
                    for wi, width in enumerate(ws):
                        features = query_features(D, width)
                        lhs = 1 - features @ Yc
                        norm = np.linalg.norm(features, axis=1)
                        for li, lower in enumerate(lows):
                            for mi, method in enumerate(METHODS):
                                cm = masks[wi, li, mi]
                                row = local_cert_rows[(local_cert_rows.width_index == wi) & (local_cert_rows.lambda_lower == lower) & (local_cert_rows.method == method)]
                                assert len(row) == 1 and int(row.certified.iloc[0]) == int(cm.sum())
                                rec = dict(dataset=dataset, seed=seed, K=K, width_index=wi,
                                           lambda_lower=int(lower), method=method, certified=int(cm.sum()),
                                           near_nearest_distance_ties=near_ties,
                                           minimum_certified_raw_margin=None,
                                           minimum_certified_margin_guard_ratio=None)
                                if cm.any():
                                    rhs = norm[:, None] * bounds[wi, li, mi, nn]
                                    gaps = lhs - rhs
                                    guard = protocol['strict_guard'] * (1 + abs(lhs) + abs(rhs))
                                    ratios = gaps / guard
                                    gaps[np.arange(len(nn)), nn] = np.inf
                                    ratios[np.arange(len(nn)), nn] = np.inf
                                    min_by_query = gaps.min(axis=1)
                                    assert np.allclose(saved_gaps[wi, li, mi, cm], min_by_query[cm], rtol=1e-12, atol=1e-14)
                                    min_margin = float(min_by_query[cm].min())
                                    min_ratio = float(ratios.min(axis=1)[cm].min())
                                    assert min_ratio > 1
                                    rec['minimum_certified_raw_margin'] = min_margin
                                    rec['minimum_certified_margin_guard_ratio'] = min_ratio
                                    if min_margin_cell is None or min_margin < min_margin_cell['minimum_certified_raw_margin']:
                                        min_margin_cell = rec.copy()
                                    if min_ratio_cell is None or min_ratio < min_ratio_cell['minimum_certified_margin_guard_ratio']:
                                        min_ratio_cell = rec.copy()
                                numeric.append(rec)
                                for fraction in protocol['width_probe_fractions']:
                                    pi = int(np.argmin(abs(probe_widths - width * fraction)))
                                    for penalty in protocol['lambda_probe_rule'][str(int(lower))]:
                                        lj = int(np.flatnonzero(penalties == penalty)[0])
                                        tested[mi, pi, lj] |= cm
                    for mi, method in enumerate(METHODS):
                        method_dedup_counts[method] += int(tested[mi].sum())
                    union = np.any(tested, axis=0)
                    all_method_union_comparisons += int(union.sum())
                    all_method_union_violations += int(np.sum(union & (predictions != nn)))
                    groups.append(dict(dataset=dataset, seed=seed, K=K, query_n=len(nn),
                                       numerical_rank_min=int(ranks.min()), numerical_rank_max=int(ranks.max()),
                                       all_probe_matrices_full_rank=bool(np.all(ranks == K)),
                                       distinct_prototype_images=int(len(np.unique(flatten(images[z['center_ids']]), axis=0))),
                                       near_nearest_distance_ties=near_ties,
                                       sharp_basic_masks_identical=equal, masks_nested=nested,
                                       distinct_certified_query_parameter_comparisons=int(union.sum()),
                                       probe_width_count=len(probe_widths), probe_penalty_count=len(penalties)))
    assert all_method_union_violations == 0
    add_widths(pd.DataFrame(numeric)).to_csv(HERE / 'appendix_numerical_guard_audit.csv', index=False)
    pd.DataFrame(groups).to_csv(HERE / 'appendix_group_audit.csv', index=False)

    per_method = []
    for keys, cell in cert.groupby(['dataset', 'method'], sort=True):
        per_method.append(dict(dataset=keys[0], method=keys[1], declared_seed_condition_cells=len(cell),
                               evaluated_query_rectangles=int(cell.n.sum()),
                               certified_query_rectangles=int(cell.certified.sum()),
                               finite_certified_rectangle_probe_comparisons=int((cell.certified * cell.probe_pairs).sum()),
                               zero_coverage_cells=int(cell.certified.eq(0).sum()),
                               inapplicable_cells=int((~cell.applicable).sum())))
    summary = dict(
        analysis_utc=datetime.now(timezone.utc).isoformat(), completed=complete,
        verified_result_manifest_files=len(manifest), analysis_source_sha256=sha(__file__),
        query_denominators={'mnist': 4027, 'fashion_mnist': 10000}, seeds=[11, 22, 33, 44, 55],
        dataset_seed_budget_groups=30, seeds_per_summary=5,
        certificate_method_cells=len(cert), endpoint_cells=len(end),
        distinct_region_cells_without_method=len(end),
        evaluated_method_query_rectangles=int(cert.n.sum()),
        evaluated_query_rectangles_without_method=int(cert.loc[cert.method == 'sharp', 'n'].sum()),
        certified_method_query_rectangles=int(cert.certified.sum()),
        certified_query_rectangles_without_method=int(cert.loc[cert.method == 'sharp', 'certified'].sum()),
        finite_certified_method_rectangle_probe_comparisons=int((cert.certified * cert.probe_pairs).sum()),
        finite_certified_sharp_rectangle_probe_comparisons=int((cert.loc[cert.method == 'sharp', 'certified'] * 9).sum()),
        distinct_certified_query_parameter_comparisons_within_group=all_method_union_comparisons,
        distinct_certified_query_parameter_comparisons_within_group_by_method=method_dedup_counts,
        finite_probe_violations=int(cert.certified_probe_violations.sum()),
        deduplicated_finite_probe_violations=all_method_union_violations,
        zero_coverage_method_cells=int(cert.certified.eq(0).sum()),
        inapplicable_method_cells=int((~cert.applicable).sum()),
        all_absolute_width_one_cells_zero=bool(cert.loc[cert.width_index == 0, 'certified'].eq(0).all()),
        all_scaled_width_one_eighth_through_two_cells_zero=bool(cert.loc[cert.width_index >= 2, 'certified'].eq(0).all()),
        sharp_basic_masks_identical=bool(all_masks_equal),
        frobenius_subset_basic_subset_sharp=bool(all_masks_nested),
        maximum_sharp_minus_basic_pp=float(pair.sharp_minus_basic_pp.max()),
        maximum_sharp_minus_frobenius_pp=float(pair.sharp_minus_frobenius_pp.max()),
        minimum_certified_margin_cell=min_margin_cell,
        minimum_certified_margin_guard_ratio_cell=min_ratio_cell,
        all_probe_matrices_full_rank=bool(all(g['all_probe_matrices_full_rank'] for g in groups)),
        all_groups_have_distinct_prototype_images=bool(all(g['distinct_prototype_images'] == g['K'] for g in groups)),
        near_nearest_tie_queries_summed_over_groups=int(sum(g['near_nearest_distance_ties'] for g in groups)),
        per_dataset_method=per_method,
        counting_notes=[
            'A query rectangle is one query within one dataset/seed/budget/width-bound/penalty-floor condition.',
            'Method-tagged counts additionally repeat each rectangle for sharp, basic, and Frobenius.',
            'There are nine finite probes per rectangle. Repeated rectangle/probe counts may revisit the same query and parameter pair.',
            'Distinct query/parameter counts deduplicate overlapping rectangles and methods within each dataset/seed/budget group; seeds and budgets remain separate.',
            'Five seeds share evaluation subjects. Mean and sample SD describe seed realizations. Grid cells and probes are not independent population samples.',
            'Finite agreement checks verify implementation on sampled parameter points; the analytical theorem supplies the continuous-region guarantee.',
            'Accuracy uses ground-truth labels at the upper-width/lower-penalty endpoint. Agreement compares readout and nearest-prototype labels at that endpoint.'
        ])
    dump('summary.json', summary)
    dump('source_trace.json', dict(analysis_source_sha256=sha(__file__),
         result_manifest_sha256=sha(R / 'MANIFEST_SHA256.json'), frozen_sources=freeze,
         inputs={str(R.relative_to(ROOT) / p): h for p, h in manifest.items()},
         numerical_audit_image_sources={name: h for name, h in protocol['data_sha256'].items()},
         provenance='Aggregate tables read frozen CSV counts. Mask equality, inclusion, distinct finite probes, numerical ranks and guards read archived NPZ predictions and recomputed query features; no readout is fitted.'))
    write_report(summary, cov, ends)
    plot_figures(cert, end)
    outputs = sorted(p for p in HERE.rglob('*') if p.is_file() and p.name != 'OUTPUT_SHA256.json')
    dump('OUTPUT_SHA256.json', {str(p.relative_to(HERE)): sha(p) for p in outputs})
    print(json.dumps({k: summary[k] for k in [
        'certified_query_rectangles_without_method', 'certified_method_query_rectangles',
        'finite_certified_sharp_rectangle_probe_comparisons',
        'finite_certified_method_rectangle_probe_comparisons',
        'distinct_certified_query_parameter_comparisons_within_group',
        'finite_probe_violations', 'minimum_certified_margin_cell',
        'minimum_certified_margin_guard_ratio_cell']}, indent=2))


def table(cov, ends, width_indices):
    lines = ['| Dataset | K | Width upper bound | Penalty floor | Sharp / basic coverage (%) | Frobenius coverage (%) | Zero seeds: sharp / Frobenius | Endpoint agreement (%) | Readout accuracy (%) |',
             '|---|---:|---|---:|---:|---:|---:|---:|---:|']
    for _, row in ends.loc[ends.width_index.isin(width_indices)].iterrows():
        matched = cov.loc[(cov[KEYS] == row[KEYS]).all(axis=1)].set_index('method')
        sharp, frob = matched.loc['sharp'], matched.loc['cancellation_frobenius']
        w = '1 (absolute)' if row.width_index == 0 else f'{MULTIPLIERS[int(row.width_index)]:g} × s_C'
        lines.append(f"| {DATASET_NAMES[row.dataset]} | {int(row.K)} | {w} | {int(row.lambda_lower)} | {sharp.coverage_mean_percent:.3f} ± {sharp.coverage_sample_sd_pp:.3f} | {frob.coverage_mean_percent:.3f} ± {frob.coverage_sample_sd_pp:.3f} | {int(sharp.zero_coverage_seeds)} / {int(frob.zero_coverage_seeds)} | {row.nearest_readout_agree_mean_percent:.3f} ± {row.nearest_readout_agree_sample_sd_pp:.3f} | {row.readout_correct_mean_percent:.3f} ± {row.readout_correct_sample_sd_pp:.3f} |")
    return lines


def write_report(s, cov, ends):
    lines = ['# Frozen experiment: descriptive results', '',
        'The sharp and basic certificates produce identical masks over the complete predeclared experiment. Positive coverage occurs only at the smallest scaled upper width, s_C/16. All methods abstain at absolute upper width 1 and at scaled upper widths s_C/8 through 2s_C.', '',
        'Every table uses all five seeds, including zero-coverage realizations. Entries are mean ± sample standard deviation in percentage points, with five seeds on shared evaluation queries: 4,027 MNIST reserve images and 10,000 Fashion-MNIST test images. No sampling confidence intervals or independent grid-cell inference are used.', '',
        '## Exact denominator and audit accounting', '',
        f"The experiment contains {s['dataset_seed_budget_groups']} dataset/seed/budget groups, {s['endpoint_cells']} parameter-region cells, and {s['certificate_method_cells']} method-tagged cells. There are {s['evaluated_query_rectangles_without_method']:,} query rectangles across those conditions; {s['certified_query_rectangles_without_method']:,} are certified by sharp and basic. The Frobenius set is a subset in every cell.", '',
        f"Sharp alone contributes {s['finite_certified_sharp_rectangle_probe_comparisons']:,} certified rectangle/probe comparisons. Counting all three methods gives {s['certified_method_query_rectangles']:,} certified method/query rectangles and {s['finite_certified_method_rectangle_probe_comparisons']:,} certified method/rectangle/probe comparisons. Deduplicating overlapping rectangles and methods within each dataset/seed/budget group gives {s['distinct_certified_query_parameter_comparisons_within_group']:,} query/parameter comparisons. Every count has zero observed disagreements. These repeated-query checks assess the implementation at finite parameter values; the theorem establishes the continuum guarantee.", '',
        f"All {s['verified_result_manifest_files']} frozen result hashes match. {s['zero_coverage_method_cells']} of {s['certificate_method_cells']} method cells have zero coverage; {s['inapplicable_method_cells']} are inapplicable under the declared positive-denominator condition. Both categories remain in every denominator.", '',
        '## Main table: predeclared absolute width and smallest scaled width', '']
    lines += table(cov, ends, [0, 1])
    lines += ['', '## Numerical checks', '',
        f"The minimum certified unscaled margin is {s['minimum_certified_margin_cell']['minimum_certified_raw_margin']:.12g}; its cell is {s['minimum_certified_margin_cell']}. The smallest ratio of a certified margin to the declared numerical guard is {s['minimum_certified_margin_guard_ratio_cell']['minimum_certified_margin_guard_ratio']:.12g}. All 30 groups have distinct prototype images, and all 480 probed feature matrices have full numerical column rank under the frozen SVD threshold.", '',
        '## Evidence and source trace', '',
        '`certificate_metrics_before_labels.csv` supplies certificate counts and region applicability. `endpoint_accuracy_and_fidelity.csv` supplies agreement and true-label accuracy counts. `certificate_accuracy.csv` supplies certified-subset correctness, with undefined conditional accuracy retained as an empty field when the certified set is empty. Archived `predictions_before_labels.npz` files establish exact mask equality, subset nesting, finite-probe deduplication, and numerical margins. `source_trace.json` records all input hashes. `analyze.py` reproduces all analysis tables and figures without changing or fitting the archived models.', '',
        '## Limitations', '',
        'Five seed realizations share evaluation queries, so the stated SD measures seed variation. The certified events guarantee agreement with the nearest-prototype label, and endpoint classification accuracy is measured separately against the dataset label. All bounds and audits use float64 arithmetic; outward-rounded interval verification is outside this execution. The selected data are two image benchmarks and random prototype subsets. Absolute width 1 and all scaled widths at least s_C/8 have zero observed certificate coverage. The sharp bound gives no realized mask improvement over the basic bound in this grid.']
    (HERE / 'summary.md').write_text('\n'.join(lines) + '\n')
    appendix = ['# All predeclared parameter conditions', '',
        'Mean ± sample SD across five seed realizations. All zero-coverage seeds remain in the summaries. Full per-seed counts appear in the corresponding CSV files.', ''] + table(cov, ends, range(7))
    (HERE / 'appendix_all_grid_tables.md').write_text('\n'.join(appendix) + '\n')


def plot_figures(cert, end):
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    from matplotlib.lines import Line2D
    plt.rcParams.update({'font.family': 'DejaVu Sans', 'font.size': 9,
                         'axes.labelsize': 9, 'axes.titlesize': 10,
                         'xtick.labelsize': 9, 'ytick.labelsize': 9,
                         'legend.fontsize': 9, 'pdf.fonttype': 42, 'ps.fonttype': 42,
                         'svg.fonttype': 'path', 'savefig.facecolor': 'white',
                         'axes.spines.top': False, 'axes.spines.right': False,
                         'axes.edgecolor': '#73818e', 'xtick.color': '#273747',
                         'ytick.color': '#273747', 'text.color': '#132d46',
                         'axes.labelcolor': '#132d46'})
    navy, teal, gray = '#173b60', '#008b8b', '#7c8793'
    xticks = np.arange(6)
    labels = ['1/16', '1/8', '1/4', '1/2', '1', '2']
    seed_jitter = np.linspace(-.055, .055, 5)

    def axes_grid():
        fig, axes = plt.subplots(2, 3, figsize=(7.2, 4.8), sharex=True, sharey=True)
        fig.subplots_adjust(left=.095, right=.985, bottom=.13, top=.83, hspace=.34, wspace=.13)
        for i, dataset in enumerate(DATASETS):
            for j, floor in enumerate(FLOORS):
                ax = axes[i, j]
                ax.set_xlim(-.22, 5.17); ax.set_ylim(-4, 104)
                ax.set_xticks(xticks, labels)
                ax.set_yticks([0, 25, 50, 75, 100])
                ax.grid(axis='y', color='#e3e8ed', linewidth=.6)
                ax.set_axisbelow(True)
                ax.set_title(f"{'abcdef'[3*i+j]}   {DATASET_NAMES[dataset]}  |  $\\lambda_0={floor}$", loc='left', pad=8)
        for ax in axes[-1]: ax.set_xlabel(r'Upper width / $s_C$')
        return fig, axes

    fig, axes = axes_grid()
    for i, dataset in enumerate(DATASETS):
        for j, floor in enumerate(FLOORS):
            ax = axes[i, j]
            for method, color, marker, offset, style in [
                ('sharp', navy, 'o', -.035, '-'),
                ('cancellation_frobenius', teal, 's', .035, '--')]:
                cell = cert[(cert.dataset == dataset) & (cert.K == 100) & (cert.lambda_lower == floor) & (cert.method == method) & (cert.width_index > 0)]
                means = cell.groupby('width_index').coverage_percent.mean().reindex(range(1, 7)).to_numpy()
                for wi in range(1, 7):
                    values = cell.loc[cell.width_index == wi].sort_values('seed').coverage_percent.to_numpy()
                    ax.scatter(wi - 1 + seed_jitter + offset, values, s=13, marker=marker,
                               facecolors='none', edgecolors=color, alpha=.55, linewidths=.7, zorder=3)
                ax.plot(xticks + offset, means, color=color, marker=marker, markersize=4,
                        linewidth=1.4, linestyle=style, zorder=4)
            narrow = cert[(cert.dataset == dataset) & (cert.K == 100) &
                          (cert.lambda_lower == floor) & (cert.width_index == 1)]
            zero_sharp = int(narrow.loc[narrow.method == 'sharp', 'certified'].eq(0).sum())
            zero_frob = int(narrow.loc[narrow.method == 'cancellation_frobenius', 'certified'].eq(0).sum())
            ax.text(.34, .61,
                    f'Zero seeds at 1/16\nSharp/basic: {zero_sharp}/5\nFrobenius: {zero_frob}/5',
                    transform=ax.transAxes, fontsize=9, color='#465b70',
                    linespacing=1.4, va='top')
            if j == 0: ax.set_ylabel('Certified queries (%)')
    handles = [Line2D([0], [0], color=navy, marker='o', lw=1.4, label='Sharp / basic mean'),
               Line2D([0], [0], color=teal, marker='s', lw=1.4, linestyle='--', label='Frobenius mean'),
               Line2D([0], [0], color=gray, marker='o', markerfacecolor='none', lw=0, label='Individual seed')]
    fig.legend(handles=handles, loc='upper center', bbox_to_anchor=(.5, .965), ncol=3, frameon=False, columnspacing=1.5)
    for ext in ['pdf', 'svg', 'png']:
        fig.savefig(FIG / f'figure1_coverage_profiles.{ext}', dpi=300)
    plt.close(fig)

    fig, axes = axes_grid()
    for i, dataset in enumerate(DATASETS):
        for j, floor in enumerate(FLOORS):
            ax = axes[i, j]
            cell = end[(end.dataset == dataset) & (end.K == 100) & (end.lambda_lower == floor) & (end.width_index > 0)]
            for metric, color, marker, offset in [('nearest_readout_agree', navy, 'o', -.025),
                                                 ('readout_correct', teal, 's', .025)]:
                means = cell.groupby('width_index')[metric + '_percent'].mean().reindex(range(1, 7)).to_numpy()
                for wi in range(1, 7):
                    values = cell.loc[cell.width_index == wi].sort_values('seed')[metric + '_percent'].to_numpy()
                    ax.scatter(wi - 1 + seed_jitter + offset, values, s=10, marker=marker,
                               facecolors='none', edgecolors=color, alpha=.38, linewidths=.6, zorder=3)
                ax.plot(xticks + offset, means, color=color, marker=marker, markersize=4, lw=1.4, zorder=4)
            nearest_mean = cell.loc[cell.width_index == 1, 'nearest_correct_percent'].mean()
            ax.axhline(nearest_mean, color=gray, linestyle=':', lw=1.2, zorder=2)
            if j == 0: ax.set_ylabel('Evaluation queries (%)')
    handles = [Line2D([0], [0], color=navy, marker='o', lw=1.4, label='Nearest-label agreement'),
               Line2D([0], [0], color=teal, marker='s', lw=1.4, label='Readout accuracy'),
               Line2D([0], [0], color=gray, lw=1.2, linestyle=':', label='Nearest-label accuracy')]
    fig.legend(handles=handles, loc='upper center', bbox_to_anchor=(.5, .965), ncol=3, frameon=False, columnspacing=1.3)
    for ext in ['pdf', 'svg', 'png']:
        fig.savefig(FIG / f'figure2_agreement_accuracy.{ext}', dpi=300)
    plt.close(fig)
    captions = '''# Publication figure captions

**Figure 1. Coverage of continuous parameter-region certificates.** Each panel reports K=100 prototypes and one penalty floor, using every predeclared scaled upper width. Each certified query is guaranteed to retain its nearest-prototype label for all 0 < sigma <= t and lambda >= lambda_0. Lines join the mean percentages across five seeds; hollow markers show the five individual seed values, with small horizontal offsets for visibility. Sharp and basic masks are identical over the entire experiment and are represented by one curve. The Frobenius comparison uses the same parameter region and queries. All zero outcomes remain visible, including zero-coverage seed realizations at t=s_C/16. The fixed absolute width t=1 is reported in the main table and has zero coverage for every method, budget, floor, and seed. Each seed evaluates the same 4,027 MNIST reserve images or 10,000 Fashion-MNIST test images; the seed points are repeated experiments on shared queries. Here s_C is the median pairwise prototype distance divided by sqrt(2).

**Figure 2. Endpoint label agreement and classification accuracy answer different questions.** For every scaled width and each penalty floor, the endpoint is (sigma, lambda)=(t, lambda_0), with K=100. Navy curves report agreement between the fitted readout and nearest-prototype labels. Teal curves report fitted-readout accuracy against the dataset labels. Dotted lines give nearest-prototype accuracy, which is independent of sigma and lambda for a fixed seed. Lines are means over all five seeds; hollow markers show individual seed values, with small horizontal offsets. The same 4,027 MNIST reserve images or 10,000 Fashion-MNIST test images are used across seeds. Endpoint agreement is an observed finite-point quantity; Figure 1 reports certification over whole parameter regions. All six scaled widths and all three penalty floors are included.

**Production specification.** Figures are 7.2 x 4.8 inches, with 9 pt or larger labels and DejaVu Sans. PDF files embed TrueType fonts; SVG files convert glyphs to vector paths for portable rendering; PNG previews use 300 dpi. Statistical variability is shown with individual seed values rather than intervals that extend beyond the bounded 0–100% outcome range. The coverage panels also state the number of zero-coverage seeds at the smallest scaled width. All means and sample SDs, including zeros, are provided in the corresponding CSV tables.
'''
    (HERE / 'figure_captions.md').write_text(captions)


if __name__ == '__main__':
    main()
