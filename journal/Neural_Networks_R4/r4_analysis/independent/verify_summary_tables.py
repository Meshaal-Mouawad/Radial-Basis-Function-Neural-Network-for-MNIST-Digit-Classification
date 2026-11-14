#!/usr/bin/env python3
"""Check final E/G descriptive tables against independently audited arrays."""
import csv,hashlib,json
from pathlib import Path
import numpy as np
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[1];OUT=ROOT/'r4_analysis/competitive/results';PATHS=ROOT/'r4_analysis/disagreement/results'
def read(name):
    with (OUT/name).open() as f:return list(csv.DictReader(f))
def eq(x,y):assert abs(float(x)-float(y))<1e-9,(x,y)
def audit_mean(rows,summary,keys):
    for k in keys:
        a=np.array([float(x[k]) for x in rows]);eq(a.mean(),summary[k+'_mean']);eq(a.std(ddof=1),summary[k+'_sd'])

def main():
    # Require all three independent core audits, performed from original data.
    for name in ['composition_verification.json','competitive_verification.json','paths_efficiency_verification.json']:
        assert json.loads((HERE/name).read_text())['status']=='PASS'
    best=read('validation_best_per_seed.csv');sets=read('competitive_sets_per_seed.csv');paired=read('budget_paired_per_seed.csv');retained={q:0 for q in [.9,.95,.99]};zero={q:0 for q in retained};groups=0
    for p in sorted(OUT.glob('*_K*.npz')):
        ds,rest=p.stem.split('_seed');ss,K=rest.split('_K');seed=int(ss);K=int(K)
        with np.load(p) as z:
            correct=(z['predictions']==z['truth']).mean(2)*100;agreement=(z['predictions']==z['nearest_prototype']).mean(2)*100;coverage=z['certificate'].mean(2)*100;excluded=z['excluded_region'].mean(2)*100;validation=z['validation_correct']/len(z['validation_ids'])*100
            for qi,q in enumerate([.9,.95,.99]):
                mask=z['competitive'][qi];r=next(x for x in sets if x['dataset']==ds and int(x['seed'])==seed and int(x['K'])==K and float(x['threshold'])==q)
                for name,values in [('evaluation_accuracy_pct',correct),('agreement_pct',agreement),('certificate_coverage_pct',coverage),('region_exclusion_pct',excluded),('validation_accuracy_pct',validation)]:
                    a=values[mask];eq(a.min(),r[name+'_min']);eq(a.mean(),r[name+'_mean']);eq(a.max(),r[name+'_max'])
                retained[q]+=int(mask.sum());zero[q]+=int(not z['certificate'][mask].any())
        groups+=1
    assert groups==30
    for r in read('validation_best_summary.csv'):
        rr=[x for x in best if x['dataset']==r['dataset'] and x['K']==r['K']];assert len(rr)==5
        audit_mean(rr,r,['validation_accuracy_pct','evaluation_accuracy_pct','nearest_accuracy_pct','nearest_agreement_pct','certificate_coverage_pct','combined_region_exclusion_pct','sigma_over_sC','penalty'])
    for r in read('competitive_sets_summary.csv'):
        rr=[x for x in sets if x['dataset']==r['dataset'] and x['K']==r['K'] and x['threshold']==r['threshold']];assert len(rr)==5
        eq(sum(int(x['retained_models']) for x in rr),r['retained_models_total']);eq(sum(x['all_retained_zero_coverage']=='True' for x in rr),r['groups_all_zero_coverage']);eq(sum(int(x['certified_query_model_count']) for x in rr),r['certified_query_model_count'])
        audit_mean(rr,r,['retained_models','evaluation_accuracy_pct_mean','agreement_pct_mean','certificate_coverage_pct_mean','region_exclusion_pct_mean'])
    for r in read('budget_paired_summary.csv'):
        rr=[x for x in paired if x['dataset']==r['dataset'] and x['K_low']==r['K_low'] and x['K_high']==r['K_high']];assert len(rr)==5
        audit_mean(rr,r,['evaluation_accuracy_difference_pp','validation_accuracy_difference_pp','nearest_agreement_difference_pp','prediction_disagreement_pct','correctness_jaccard']);eq(sum(float(x['evaluation_accuracy_difference_pp'])>0 for x in rr),r['seeds_positive_accuracy_difference'])
    return_cases=0;path_cases=0;max_changes=0;guard_cases=0;invalid_cases=0
    for p in sorted(PATHS.glob('*_paths.npz')):
        with np.load(p) as z:
            return_cases+=int(np.count_nonzero(z['sampled_return_to_agreement_count']>0));path_cases+=z['first_disagreement_index'].size;max_changes=max(max_changes,int(z['sampled_sign_change_count'].max()));guard_cases+=int(z['any_guard_sample'].sum());invalid_cases+=int(z['any_invalid_sample'].sum())
    inputs={}
    for folder,patterns in [(OUT,['*.npz','*.csv']),(PATHS,['*_paths.npz','*_finite_masks.npz','*.csv']),(ROOT/'next_work/results',['*.csv'])]:
        for pat in patterns:
            for p in sorted(folder.glob(pat)):inputs[str(p.relative_to(ROOT))]=hashlib.sha256(p.read_bytes()).hexdigest()
    report=dict(status='PASS',groups=groups,validation_best_summary_rows=6,competitive_summary_rows=18,budget_paired_summary_rows=6,retained_model_counts={str(q):retained[q] for q in retained},zero_coverage_groups={str(q):zero[q] for q in zero},sampled_return_to_agreement_query_width_cases=return_cases,all_query_width_cases=path_cases,maximum_sampled_sign_changes=max_changes,guard_query_width_cases=guard_cases,invalid_query_width_cases=invalid_cases,verified_output_sha256=inputs,script_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest())
    (HERE/'summary_tables_verification.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({k:v for k,v in report.items() if k!='verified_output_sha256'},indent=2))

if __name__=='__main__':main()
