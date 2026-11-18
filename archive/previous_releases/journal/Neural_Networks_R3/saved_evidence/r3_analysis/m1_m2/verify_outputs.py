#!/usr/bin/env python3
"""Read-only recheck of R3 outputs and sampled direct-solve bound reversals."""
import csv, gzip, json
from pathlib import Path
import numpy as np
from scipy.io import loadmat
from scipy.spatial.distance import cdist
from threadpoolctl import threadpool_limits
from run_analysis import HERE,ROOT,BASE,EXP,DIAG,sha,flatten,idx

def main():
    out=HERE/'results';manifest=json.loads((out/'SHA256_MANIFEST.json').read_text())
    for name,value in manifest.items(): assert sha(out/name)==value,name
    rows=list(csv.DictReader((out/'m2_overlap_per_seed.csv').open()))
    r2={(r['dataset'],int(r['seed']),int(r['width_index']),int(r['lambda_floor'])):r for r in csv.DictReader((DIAG/'original7_guarded/rectangles.csv').open())}
    comparisons=0;solve_checks=0;minmargin=np.inf
    with threadpool_limits(1):
      for ds in ['mnist','fashion_mnist']:
        if ds=='mnist':
            mat=loadmat(BASE/'repository/Code/MNIST_train.mat');images=mat['imagestrain'].transpose(2,0,1);labels=mat['labelstrain'].ravel().astype(int)
            qimages=images[np.load(BASE/'work/v2/design/reserved_training_ids.npy')]
        else:
            folder=BASE/'work/v2/data/fashion_mnist';images=idx(folder/'train-images-idx3-ubyte.gz');qimages=idx(folder/'t10k-images-idx3-ubyte.gz');labels=np.frombuffer(gzip.decompress((folder/'train-labels-idx1-ubyte.gz').read_bytes()),np.uint8,offset=8)
        Xq=flatten(qimages)
        for seed in [11,22,33,44,55]:
            name=f'{ds}_seed{seed}_K100'
            with np.load(EXP/name/'predictions_before_labels.npz') as orig:
                X=flatten(images[orig['train_ids']]);C=flatten(images[orig['center_ids']]);Y=np.eye(10)[labels[orig['train_ids']]];center_rows=orig['center_rows']
            Dt=cdist(X,C,'sqeuclidean');Dq=cdist(Xq,C,'sqeuclidean');Dq-=Dq.min(1,keepdims=True)
            with np.load(out/f'{name}.npz') as z:
                rr=[r for r in rows if r['dataset']==ds and int(r['seed'])==seed]
                for r in rr:
                    wi=int(r['width_index']);fl=int(r['penalty_floor']);li=[0,1,100].index(fl);L=z['original_limit_prefix'][wi];Ld=z['dense_limit_prefix'][wi];F=z['finite_original'][wi,li];Fa=z['finite_all_archived'][wi,li]
                    masks={'r2_union':L|F,'r2_limit_only_vs_original':L&~F,'r2_limit_only_vs_all':L&~Fa,'limit_only_vs_all':Ld&~Fa,'combined_full':Ld|Fa,'all_archived_finite':Fa}
                    for field,m in masks.items(): assert int(m.sum())==int(r[field]);comparisons+=1
                    assert int(r['r2_union'])==int(r2[(ds,seed,wi,fl)]['combined_excluded'])
                for wi,w in enumerate(z['widths']):
                    th=z['threshold'][wi];finite=np.flatnonzero(np.isfinite(th));sel=finite[np.unique(np.linspace(0,len(finite)-1,min(5,len(finite))).astype(int))] if len(finite) else []
                    H=np.exp(-Dt/(2*w*w));H[center_rows,np.arange(100)]=1;A=H.T@H;Z=H.T@Y
                    for q in sel:
                        a=z['nearest_prototype'][q];b=z['best_competing_class'][wi,q];r=np.exp(-Dq[q]/(2*w*w));v=Z[:,b]-Z[:,a]
                        bound=np.linalg.norm(r)*np.linalg.norm(A@v)/(r@v)
                        assert np.isclose(bound,th[q],rtol=1e-9,atol=1e-10)
                        lam=1.001*th[q];actual=lam*r@np.linalg.solve(A+lam*np.eye(100),v)
                        assert actual>0;solve_checks+=1;minmargin=min(minmargin,float(actual))
    result=dict(status='PASS',manifest_files=len(manifest),mask_count_comparisons=comparisons,r2_region_counts_matched=len(rows),sampled_direct_solve_threshold_checks=solve_checks,minimum_scaled_competing_margin=minmargin)
    print(json.dumps(result,indent=2))

if __name__=='__main__':main()
