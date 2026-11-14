#!/usr/bin/env python3
"""Read-only integrity and scientific-array verification; no model fitting."""
import argparse,csv,hashlib,json
from pathlib import Path
import numpy as np
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
STAGES=('original7_guarded','dense67_guarded','local_tail','local_tail_validation')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def manifest(root,path):
    obj=json.loads(path.read_text())
    for name,value in obj.items():assert sha(root/name)==value, name
    return len(obj)
def main():
    ap=argparse.ArgumentParser();ap.add_argument('--compare-reproduction',type=Path);a=ap.parse_args()
    report={'canonical_files_checked':manifest(HERE,HERE/'FINAL_MANIFEST_SHA256.json'),'baseline_inputs_checked':manifest(ROOT,HERE/'INPUT_SHA256.json')}
    for stage in STAGES:manifest(HERE/stage,HERE/stage/'MANIFEST_SHA256.json')
    for stage in STAGES[:2]:
        for p in (HERE/stage).glob('*.npz'):
            with np.load(p) as z:
                cm=z['sharp_certificate_masks'];ex=z['prefix_obstruction'][:,None,:]|z['finite_probe_obstruction'];assert not np.any(cm&ex)
                assert np.array_equal(z['endpoint_obstruction'],z['limit_competing_minus_nearest']>z['sign_guard'])
                if stage=='dense67_guarded':
                    assert np.all(~cm[1:]|cm[:-1]);assert np.all(~z['prefix_obstruction'][:-1]|z['prefix_obstruction'][1:])
    count=0
    for p in (HERE/'local_tail').glob('*.npz'):
        with np.load(p) as z, np.load(HERE/'local_tail_validation'/p.name) as v:
            for case in range(4):
                positive=z[f'case{case}_positive_margin_mask'];th=z[f'case{case}_threshold'];simple=z[f'case{case}_simple_threshold'];assert np.all(th[positive]<=simple[positive]*(1+1e-12));assert np.all(np.isinf(th[~positive]));assert np.array_equal(positive,np.all(z[f'case{case}_margins']>z[f'case{case}_margin_guard'],axis=1))
                op=float(np.linalg.eigvalsh(z[f'case{case}_A_t'])[-1]);pred=v[f't{case//2}_predictions'];start=1 if case%2==0 else 0
                for li,mult in enumerate([10,100]):
                    mask=th<=mult*op
                    for si in range(start,3):assert not np.any(mask&(pred[li,si]!=v['nearest_prototype']));count+=int(mask.sum())
    assert count==254120;report['certified_numerical_checks']=count;report['certified_disagreements']=0
    if a.compare_reproduction:
        other=a.compare_reproduction.resolve();arrays=0;csvfiles=0
        for stage in STAGES:
            for p in (HERE/stage).glob('*.npz'):
                with np.load(p) as z,np.load(other/stage/p.name) as zz:
                    assert set(z.files)==set(zz.files)
                    for key in z.files:assert np.array_equal(z[key],zz[key]),(stage,p.name,key);arrays+=1
            for p in (HERE/stage).glob('*.csv'):
                assert p.read_text()==(other/stage/p.name).read_text(),str(p);csvfiles+=1
        assert (HERE/'manuscript_claim_count_audit.json').read_text()==(other/'manuscript_claim_count_audit.json').read_text()
        report['exact_reproduced_arrays']=arrays;report['exact_reproduced_csv_files']=csvfiles
    report['status']='PASS';print(json.dumps(report,indent=2))
if __name__=='__main__':main()
