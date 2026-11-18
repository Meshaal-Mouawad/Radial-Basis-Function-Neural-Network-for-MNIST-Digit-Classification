#!/usr/bin/env python3
"""Separate reconstruction/count audit for the M3 outputs."""
import argparse,csv,gzip,hashlib,json,struct
from pathlib import Path
import numpy as np
from scipy.io import loadmat
from scipy.spatial.distance import cdist
from threadpoolctl import threadpool_limits
HERE=Path(__file__).resolve().parent
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def images(p):
    raw=gzip.decompress(p.read_bytes());_,n,h,w=struct.unpack('>IIII',raw[:16]);return np.frombuffer(raw,np.uint8,offset=16).reshape(n,h,w)
def flat(x):return np.asarray([a.T.ravel() for a in x],dtype=float)/255
def main():
    ap=argparse.ArgumentParser();ap.add_argument('--evidence',type=Path,default=HERE.parents[1]/'evidence');ap.add_argument('--results',type=Path,default=HERE/'results');a=ap.parse_args()
    root=a.evidence;result=a.results;base=root/'baseline/evidence/baseline';exp=base/'work/v2/experiment/results';diag=root/'new_analysis/limit_diagnostic'
    rows=list(csv.DictReader((result/'per_seed.csv').open()));classes=list(csv.DictReader((result/'class_counts.csv').open()));report=json.loads((result/'verification.json').read_text())
    for p,h in json.loads((result/'MANIFEST_SHA256.json').read_text()).items():assert sha(result/p)==h,p
    for p,h in report['inputs_sha256'].items():assert sha(root/p)==h,p
    max_weight_error=0.;max_score_error=0.;count=0;settings=0
    with threadpool_limits(1):
        for d in ['mnist','fashion_mnist']:
            if d=='mnist':
                allimgs=loadmat(base/'repository/Code/MNIST_train.mat')['imagestrain'].transpose(2,0,1);queryimgs=allimgs[np.load(base/'work/v2/design/reserved_training_ids.npy')]
            else:
                folder=base/'work/v2/data/fashion_mnist';allimgs=images(folder/'train-images-idx3-ubyte.gz');queryimgs=images(folder/'t10k-images-idx3-ubyte.gz')
            X=flat(queryimgs)
            for seed in [11,22,33,44,55]:
                name=f'{d}_seed{seed}_K100'
                with np.load(exp/name/'predictions_before_labels.npz') as archive,np.load(diag/'local_tail'/f'{name}.npz') as local,np.load(diag/'local_tail_validation'/f'{name}.npz') as validation,np.load(result/f'{name}.npz') as z:
                    center=flat(allimgs[archive['center_ids']]);scale=float(archive['width_upper_bounds'][1]*16);distance=cdist(X,center,'sqeuclidean');truth=np.load(exp/f'{d}_evaluation_labels.npy');qid=archive['query_ids'];nn=archive['nearest_prototype']
                    assert np.array_equal(truth,z['truth']) and np.array_equal(nn,z['nearest_prototype'])
                    for ri,ratio in enumerate([.5,1.]):
                        settings+=1;A=local[f'case{2*ri}_A_t'];B=local[f'case{2*ri}_B_t'];lam=10*np.linalg.eigvalsh(A)[-1];W=np.linalg.solve(A+lam*np.eye(len(A)),B)
                        max_weight_error=max(max_weight_error,float(np.max(abs(W-validation[f't{ri}_weights'][0,2]))))
                        score=np.exp(-distance/(2*(ratio*scale)**2))@W;max_score_error=max(max_score_error,float(np.max(abs(score-z[f't{ri}_raw_scores']))));p=score.argmax(axis=1);assert np.array_equal(p,z[f't{ri}_predictions'])
                        cert=z[f't{ri}_certificate_mask'];m=int(cert.sum());assert np.array_equal(cert,local[f'case{2*ri}_threshold']<=lam);assert np.all(p[cert]==nn[cert])
                        rr=[x for x in rows if x['dataset']==d and int(x['seed'])==seed and float(x['t_over_sC'])==ratio]
                        assert len(rr)==7
                        for row in rr:
                            sel=row['selector'];mask=np.ones(len(truth),bool) if sel=='full_query' else z[f't{ri}_{sel}_mask']
                            assert mask.sum()==(len(truth) if sel=='full_query' else m)
                            nc=int(mask.sum());correct=int((p[mask]==truth[mask]).sum());assert nc==int(row['selected']) and correct==int(row['correct']);assert abs(100*correct/nc-float(row['accuracy_pct']))<1e-12
                            if sel not in ['full_query','certificate']:
                                rank=z['prototype_distance_margin'] if 'distance' in sel else z[f't{ri}_normalized_margin'] if 'normalized' in sel else z[f't{ri}_score_margin']
                                candidates=[i for i in range(len(p)) if not sel.startswith('agreement_gated') or p[i]==nn[i]]
                                chosen=sorted(candidates,key=lambda i:(-float(rank[i]),int(qid[i]),i))[:m]
                                assert set(chosen)==set(np.flatnonzero(mask))
                            for k in range(10):
                                cell=[x for x in classes if x['dataset']==d and int(x['seed'])==seed and float(x['t_over_sC'])==ratio and x['selector']==sel and int(x['class_label'])==k];assert len(cell)==1
                                assert int(cell[0]['predicted_count'])==int((p[mask]==k).sum());assert int(cell[0]['true_count'])==int((truth[mask]==k).sum())
                            count+=1
    assert max_weight_error<1e-12 and max_score_error<1e-12
    out={'status':'PASS','settings_reconstructed':settings,'selector_rows_verified':count,'class_count_rows_verified':len(classes),'maximum_weight_error':max_weight_error,'maximum_score_error':max_score_error,'manifest_verified':True,'inputs_unchanged':True}
    (HERE/'independent_verification.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out))
if __name__=='__main__':main()
