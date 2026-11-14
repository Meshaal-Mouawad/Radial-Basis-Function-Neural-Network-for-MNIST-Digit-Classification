#!/usr/bin/env python3
"""Read archived records, audit manuscript claim denominators, summarize diagnostic."""
import csv,json
from pathlib import Path
import numpy as np
from run_limit_diagnostic import HERE,ROOT,EXP,FRONT,csvwrite,js

def read(p):return list(csv.DictReader(p.open()))
def main():
    audit={};certrows=read(EXP/'certificate_metrics_before_labels.csv');ends=read(EXP/'endpoint_accuracy_and_fidelity.csv')
    audit['original_certificate_records']=len(certrows);audit['original_endpoint_records']=len(ends)
    sharp=[r for r in certrows if r['method']=='sharp'];basic=[r for r in certrows if r['method']=='basic'];frob=[r for r in certrows if r['method']=='cancellation_frobenius']
    audit['sharp_certified_query_rectangles']=sum(int(r['certified']) for r in sharp);audit['frob_certified_query_rectangles']=sum(int(r['certified']) for r in frob);audit['query_rectangles_no_method']=sum(int(r['n']) for r in sharp);audit['sharp_probe_checks']=sum(int(r['certified'])*int(r['probe_pairs']) for r in sharp);audit['all_method_probe_checks']=sum(int(r['certified'])*int(r['probe_pairs']) for r in certrows);audit['sharp_finite_probe_violations']=sum(int(r['certified_probe_violations']) for r in sharp);audit['inapplicable_rectangles_no_method']=sum(r['applicable']=='False' for r in sharp)
    dedup=0;mask_equal=True
    for d in ['mnist','fashion_mnist']:
        for s in [11,22,33,44,55]:
            for k in [50,100,200]:
                with np.load(EXP/f'{d}_seed{s}_K{k}'/'predictions_before_labels.npz') as z:
                    m=z['certificate_masks'];mask_equal &= bool(np.array_equal(m[:,:,0],m[:,:,1]));union=np.zeros_like(z['predictions'],bool);pw=z['probe_widths'];pl=z['probe_penalties']
                    for wi,t in enumerate(z['width_upper_bounds']):
                        for li,lo in enumerate(z['lambda_lower_bounds']):
                            lams={0:[0,1,100],1:[1,10,100],100:[100,1000,10000]}[int(lo)]
                            for f in [.5,.75,1.]:
                                pi=int(np.flatnonzero(pw==t*f)[0])
                                for lam in lams:union[pi,int(np.flatnonzero(pl==lam)[0])]|=m[wi,li].any(axis=0)
                    dedup+=int(union.sum())
    audit['sharp_basic_all_query_masks_equal']=mask_equal;audit['deduplicated_query_parameter_checks_within_group']=dedup
    grid=read(FRONT/'grid_coverage.csv');gt={}
    for r in grid:
        if r['method'] in ['sharp','basic']:gt.setdefault((r['dataset'],r['seed'],r['K'],r['grid_index'],r['lambda_floor']),{})[r['method']]=int(r['certified'])
    diffs=[v['sharp']-v['basic'] for v in gt.values()];audit['dense_method_coverage_records']=len(grid);audit['dense_sharp_basic_conditions']=len(diffs);audit['dense_strict_sharp_gain_conditions']=sum(v>0 for v in diffs);audit['dense_total_sharp_gain_query_condition_records']=sum(diffs);audit['dense_max_gain_queries']=max(diffs)
    expected={'original_certificate_records':1890,'original_endpoint_records':630,'sharp_certified_query_rectangles':587703,'frob_certified_query_rectangles':285286,'query_rectangles_no_method':4418505,'sharp_probe_checks':5289327,'all_method_probe_checks':13146228,'sharp_finite_probe_violations':0,'inapplicable_rectangles_no_method':102,'sharp_basic_all_query_masks_equal':True,'deduplicated_query_parameter_checks_within_group':3585477,'dense_method_coverage_records':18090,'dense_sharp_basic_conditions':6030,'dense_strict_sharp_gain_conditions':35,'dense_total_sharp_gain_query_condition_records':827,'dense_max_gain_queries':382}
    assert audit==expected,(audit,expected);js(HERE/'manuscript_claim_count_audit.json',dict(status='PASS',observed=audit,reported_expected=expected,units='counts of repeated query rectangles, method-tagged grid records, or deduplicated within-group query/parameter checks as explicitly named; no sample-size interpretation'))
    dense=read(HERE/'dense67_guarded/rectangles.csv');table={(r['dataset'],int(r['seed']),int(r['lambda_floor']),int(r['width_index'])):r for r in dense};chosen=[]
    for d in ['mnist','fashion_mnist']:
        for s in [11,22,33,44,55]:
            for c in json.loads((FRONT/f'{d}_seed{s}_K100'/'chosen_endpoints_before_labels.json').read_text()):
                if c['target']!='any':continue
                for offset,name in [(0,'last_width_any_certified'),(1,'first_width_zero_certified')]:
                    r=dict(table[(d,s,c['lambda_floor'],c['grid_index']+offset)]);r['position']=name;chosen.append(r)
    csvwrite(HERE/'dense67_guarded/frontier_decomposition_per_seed.csv',chosen);summary=[]
    for d in ['mnist','fashion_mnist']:
        for lo in [0,1,100]:
            for pos in ['last_width_any_certified','first_width_zero_certified']:
                rr=[r for r in chosen if r['dataset']==d and int(r['lambda_floor'])==lo and r['position']==pos];z=dict(dataset=d,lambda_floor=lo,position=pos,seeds=5)
                for field in ['sigma_over_sC','certified','limit_prefix_excluded','finite_probe_excluded','combined_excluded','unresolved']:
                    vals=np.array([float(r[field])/(int(r['n']) if field!='sigma_over_sC' else 1)*(100 if field!='sigma_over_sC' else 1) for r in rr]);z[field+'_mean']=float(vals.mean());z[field+'_sd']=float(vals.std(ddof=1))
                summary.append(z)
    csvwrite(HERE/'dense67_guarded/frontier_decomposition_summary.csv',summary)
    print(json.dumps(audit,indent=2))
    for r in summary:
        if r['position']=='first_width_zero_certified':print(json.dumps(r))
if __name__=='__main__':main()
