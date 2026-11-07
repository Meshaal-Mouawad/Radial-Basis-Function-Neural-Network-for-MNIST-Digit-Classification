#!/usr/bin/env python3
"""Read-only descriptive analysis of the frozen continuum-certificate experiment."""
from pathlib import Path
import csv,json,hashlib,sys
import numpy as np
from scipy.io import loadmat
from scipy.spatial.distance import cdist
from collections import defaultdict
from statistics import mean,stdev
sys.path.insert(0,str(Path(__file__).resolve().parent))
from run_experiment import idx_images,flatten
from certificate import query_features,METHODS
ROOT=Path(__file__).resolve().parents[3];R=ROOT/'work/v2/experiment/results';OUT=ROOT/'work/v2/analysis';OUT.mkdir(exist_ok=True)

def read(name):
    with (R/name).open() as f:return list(csv.DictReader(f))
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def savecsv(name,rows):
    with (OUT/name).open('w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
def desc(v):return {'mean':mean(v),'sample_sd':stdev(v) if len(v)>1 else 0.,'minimum':min(v),'maximum':max(v)}
assert (R/'COMPLETE.json').exists()
manifest=json.loads((R/'MANIFEST_SHA256.json').read_text());fail=[p for p,h in manifest.items() if sha(R/p)!=h];assert not fail
cm=read('certificate_metrics_before_labels.csv');ep=read('endpoint_accuracy_and_fidelity.csv');di=read('feature_diagnostics.csv')
widthnames=['fixed1','scale_00625','scale_0125','scale_025','scale_05','scale_1','scale_2']
grouped=defaultdict(list)
for row in cm:grouped[(row['dataset'],int(row['K']),float(row['lambda_lower']),int(row['width_index']),row['method'])].append(float(row['coverage'])*100)
groups=[]
for (dataset,K,lam,wi,method),vals in sorted(grouped.items()):groups.append({'dataset':dataset,'K':K,'lambda_lower':lam,'width':widthnames[wi],'method':method,**desc(vals)})
savecsv('coverage_by_condition.csv',groups)
egroup=defaultdict(list)
for row in ep:egroup[(row['dataset'],int(row['K']),float(row['lambda_lower']),int(row['width_index']))].append(row)
eps=[]
for (dataset,K,lam,wi),rows in sorted(egroup.items()):
    rec={'dataset':dataset,'K':K,'lambda_lower':lam,'width':widthnames[wi]}
    for metric in ['readout_correct','nearest_correct','vote_correct','nearest_readout_agree','vote_readout_agree','nearest_wrong_readout_right','nearest_right_readout_wrong']:
        v=[100*int(x[metric])/int(x['n']) for x in rows];rec[metric+'_mean_percent']=mean(v);rec[metric+'_sample_sd']=stdev(v)
    eps.append(rec)
savecsv('endpoint_by_condition.csv',eps)
# Exact paired gain is calculated within each seed/setting.
cells=defaultdict(dict)
for row in cm:cells[(row['dataset'],row['seed'],row['K'],row['lambda_lower'],row['width_index'])][row['method']]=float(row['coverage'])
gains=[]
for key,v in cells.items():
    gains.append({'dataset':key[0],'seed':int(key[1]),'K':int(key[2]),'lambda_lower':float(key[3]),'width':widthnames[int(key[4])],'sharp_minus_basic_points':100*(v['sharp']-v['basic']),'sharp_minus_count_points':100*(v['sharp']-v['cancellation_frobenius'])})
savecsv('paired_coverage_gains.csv',gains)
# Numerical guard audit accesses only images, saved decisions and masks; no fitting.
protocol=json.loads((ROOT/'work/v2/experiment/protocol.json').read_text());guard=protocol['strict_guard'];numerics=[]
for dataset in protocol['datasets']:
    if dataset=='mnist':images=loadmat(ROOT/'repository/Code/MNIST_train.mat',variable_names=['imagestrain'])['imagestrain'].transpose(2,0,1);queries=images[np.load(ROOT/'work/v2/design/reserved_training_ids.npy')]
    else:images=idx_images(ROOT/'work/v2/data/fashion_mnist/train-images-idx3-ubyte.gz');queries=idx_images(ROOT/'work/v2/data/fashion_mnist/t10k-images-idx3-ubyte.gz')
    Xq=flatten(queries)
    for group in sorted(R.glob(dataset+'_seed*_K*')):
        with np.load(group/'predictions_before_labels.npz') as z:
            C=flatten(images[z['center_ids']]);D=cdist(Xq,C,'sqeuclidean');yc=z['center_labels'];Yc=np.eye(10)[yc];nn=z['nearest_prototype'];ws=z['width_upper_bounds'];lows=z['lambda_lower_bounds'];mask=z['certificate_masks'];bounds=z['pair_constants'];ranks=z['numerical_ranks'];K=int(z['K']);seed=int(z['seed']);savedg=z['certificate_min_gaps'];smallest=np.partition(D,1,axis=1)[:,:2];gapdist=smallest[:,1]-smallest[:,0];tietol=protocol['nearest_tie_relative']*np.maximum(1,np.max(smallest,axis=1));near_ties=int(np.sum(gapdist<=tietol))
            for wi,t in enumerate(ws):
                r=query_features(D,t);classmass=r@Yc;norm=np.linalg.norm(r,axis=1);lhs=1-classmass
                for li,lo in enumerate(lows):
                    for mi,method in enumerate(METHODS):
                        certified=mask[wi,li,mi]
                        minraw=None;minratio=None
                        if certified.any():
                            rhs=norm[:,None]*bounds[wi,li,mi,nn];gaps=lhs-rhs;tol=guard*(1+abs(lhs)+abs(rhs));ratio=gaps/tol;ratio[np.arange(len(nn)),nn]=np.inf;minimumratio=ratio.min(axis=1);minraw=float(savedg[wi,li,mi,certified].min());minratio=float(minimumratio[certified].min());assert minratio>1
                        numerics.append({'dataset':dataset,'seed':seed,'K':K,'width':widthnames[wi],'lambda_lower':float(lo),'method':method,'certified':int(certified.sum()),'min_certified_raw_margin':minraw,'min_certified_margin_to_guard_ratio':minratio,'near_nearest_distance_ties':near_ties,'minimum_probe_numerical_rank':int(ranks.min()),'full_rank_all_probes':bool(np.all(ranks==K))})
savecsv('numerical_guard_audit.csv',numerics)
summary={'complete':json.loads((R/'COMPLETE.json').read_text()),'verified_result_hashes':len(manifest),'manifest_failures':fail,'certificate_rows':len(cm),'total_certificate_query_rectangles':sum(int(x['n']) for x in cm),'certified_method_query_rectangles':sum(int(x['certified']) for x in cm),'finite_certified_query_parameter_checks':sum(int(x['certified'])*int(x['probe_pairs']) for x in cm),'finite_probe_violations':sum(int(x['certified_probe_violations']) for x in cm),'zero_coverage_rows':sum(int(x['certified'])==0 for x in cm),'inapplicable_rows':sum(x['applicable']=='False' for x in cm),'largest_sharp_minus_basic_points':max(x['sharp_minus_basic_points'] for x in gains),'largest_sharp_minus_count_points':max(x['sharp_minus_count_points'] for x in gains),'minimum_certified_raw_margin':min(x['min_certified_raw_margin'] for x in numerics if x['min_certified_raw_margin'] is not None),'minimum_certified_margin_to_guard_ratio':min(x['min_certified_margin_to_guard_ratio'] for x in numerics if x['min_certified_margin_to_guard_ratio'] is not None),'rank_deficient_group_rows':sum(not x['full_rank_all_probes'] for x in numerics),'prototype_duplicate_conditions':sum(int(x['distinct_prototype_images'])<int(x['K']) for x in di),'source_sha256':sha(__file__)}
(OUT/'summary.json').write_text(json.dumps(summary,indent=2)+'\n')
lines=['# Prospective continuum certificate experiment: measured results','','All values below derive from the frozen executed protocol and archived predictions. These are nearest-prototype label-agreement certificates. They do not certify true-label correctness.','',f"Completed {summary['complete']['groups']} dataset/seed/budget groups in {summary['complete']['total_seconds']:.1f} seconds. All {len(manifest)} recorded result hashes match.",'',f"Across the three methods, {summary['certified_method_query_rectangles']:,} query rectangles were certified. The finite probe audit made {summary['finite_certified_query_parameter_checks']:,} certified query/parameter comparisons and observed {summary['finite_probe_violations']} disagreements. These counts include shared queries, seeds and methods; they are implementation checks, not independent population sample sizes.",'',f"There are {summary['zero_coverage_rows']} zero-coverage certificate cells and {summary['inapplicable_rows']} inapplicable cells among {len(cm)} declared cells. All are retained.",'','## K=100 profiles (mean over five seeds; percent)','','| Dataset | lambda lower | Width upper | Sharp coverage | Basic coverage | Count coverage | Actual NN/readout agreement at endpoint | Readout accuracy |','|---|---:|---|---:|---:|---:|---:|---:|']
lookup={(x['dataset'],x['K'],x['lambda_lower'],x['width'],x['method']):x['mean'] for x in groups}
for x in eps:
 if x['K']==100:
  key=(x['dataset'],100,x['lambda_lower'],x['width']);lines.append(f"| {x['dataset']} | {x['lambda_lower']:g} | {x['width']} | {lookup[key+('sharp',)]:.3f} | {lookup[key+('basic',)]:.3f} | {lookup[key+('cancellation_frobenius',)]:.3f} | {x['nearest_readout_agree_mean_percent']:.3f} | {x['readout_correct_mean_percent']:.3f} |")
lines+=['','## Numerical and preservation checks','',f"Smallest certified raw margin: {summary['minimum_certified_raw_margin']:.6g}. Smallest certified margin/declared guard ratio: {summary['minimum_certified_margin_to_guard_ratio']:.6g}. All certified comparisons exceed the guard. This is a float64 numerical audit; no outward-rounded interval arithmetic is claimed.",f"Rows with a rank-deficient probe among their group: {summary['rank_deficient_group_rows']}. Prototype conditions containing duplicate images: {summary['prototype_duplicate_conditions']}. The per-group ranks and center counts are preserved.",'','Complete coverage, endpoint, paired-gain and numerical-guard tables are supplied as CSV. The primary result is a mathematical rectangle guarantee with measured useful coverage; finite probe agreement tests its implementation. The independent novelty/editorial decision remains a separate assessment.']
(OUT/'EVIDENCE_REPORT.md').write_text('\n'.join(lines)+'\n');print(json.dumps(summary,indent=2))
