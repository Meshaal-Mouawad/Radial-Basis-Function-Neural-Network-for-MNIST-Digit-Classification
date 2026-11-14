"""Independent reconstruction of final local-tail and strict exclusion records."""
from pathlib import Path
import json,csv,sys
import numpy as np
from scipy.io import loadmat
from scipy.spatial.distance import cdist
root=Path(__file__).resolve().parents[2]/'evidence'
work=root/'new_analysis/limit_diagnostic'
sys.path.insert(0,str(work))
from run_limit_diagnostic import BASE,EXP,idx,flatten
counts=dict(groups=0,normal_equation_checks=0,reconstructed_prediction_labels=0,certified_repeated_checks=0,guarded_rectangles=0,limit_score_checks=0)
max_resid=0.;min_margin=np.inf;count_disagreements=0
all_rows=list(csv.DictReader((work/'local_tail_validation/all_query_per_seed.csv').open()))
for ds in ['mnist','fashion_mnist']:
    if ds=='mnist':
        images=loadmat(BASE/'repository/Code/MNIST_train.mat',variable_names=['imagestrain'])['imagestrain'].transpose(2,0,1)
        qimages=images[np.load(BASE/'work/v2/design/reserved_training_ids.npy')]
    else:
        folder=BASE/'work/v2/data/fashion_mnist'
        images=idx(folder/'train-images-idx3-ubyte.gz');qimages=idx(folder/'t10k-images-idx3-ubyte.gz')
    Xq=flatten(qimages);truth=np.load(EXP/f'{ds}_evaluation_labels.npy')
    for seed in [11,22,33,44,55]:
        name=f'{ds}_seed{seed}_K100'
        with np.load(EXP/name/'predictions_before_labels.npz') as z:
            P=flatten(images[z['center_ids']]);nn=z['nearest_prototype'];yc=z['center_labels'];scale=float(z['width_upper_bounds'][1]*16)
            pw=z['probe_widths'];pl=z['probe_penalties'];ow=z['weights'];ranks=z['numerical_ranks']
        dq=cdist(Xq,P,'sqeuclidean');assert np.array_equal(yc[dq.argmin(1)],nn)
        gap=dq-dq.min(1,keepdims=True);n=len(nn);ind=np.arange(n)
        finite=np.zeros((len(pw),len(pl),n),bool)
        for i,sig in enumerate(pw):
            r=np.exp(-gap/(2*sig*sig))
            for j,lam in enumerate(pl):
                if lam==0 and ranks[i]<100:continue
                scores=r@ow[i,j];a=scores[ind,nn].copy();scores[ind,nn]=-np.inf;b=scores.max(1)
                finite[i,j]=(b-a)>1e-10*(1+abs(a)+abs(b))
        for stage in ['original7_guarded','dense67_guarded']:
            with np.load(work/stage/(name+'.npz')) as z:
                widths=z['widths'];ex=z['endpoint_obstruction'];pref=z['prefix_obstruction'];cert=z['sharp_certificate_masks']
                assert np.array_equal(ex,z['limit_competing_minus_nearest']>z['sign_guard'])
                for wi,t in enumerate(widths):
                    eligible=widths<=t*(1+1e-14)
                    assert np.array_equal(pref[wi],ex[eligible].any(0))
                    if stage=='original7_guarded':
                        scores=np.exp(-gap/(2*t*t))@z['HtY'][wi];a=scores[ind,nn].copy();scores[ind,nn]=-np.inf;b=scores.max(1)
                        assert np.allclose(a,z['nearest_limit_score'][wi],rtol=1e-13,atol=1e-12)
                        assert np.allclose(b,z['best_competing_limit_score'][wi],rtol=1e-13,atol=1e-12)
                        counts['limit_score_checks']+=n
                    pi=np.flatnonzero(pw<=t*(1+1e-14))
                    for li,floor in enumerate(z['floors']):
                        lj=np.flatnonzero(pl>=floor)
                        f=finite[pi[:,None],lj[None,:]].any((0,1)) if len(pi) else np.zeros(n,bool)
                        assert np.array_equal(f,z['finite_probe_obstruction'][wi,li])
                        assert not np.any(cert[wi,li]&(pref[wi]|f))
                        counts['guarded_rectangles']+=1
        with np.load(work/'local_tail'/(name+'.npz')) as z,np.load(work/'local_tail_validation'/(name+'.npz')) as val:
            for ri,ratio in enumerate([.5,1.]):
                t=ratio*scale;ci=2*ri;At=z[f'case{ci}_A_t'];op=np.linalg.eigvalsh(At)[-1]
                for bi,frac in enumerate([.99,.95]):
                    case=ci+bi;As=z[f'case{case}_A_s'];Bs=z[f'case{case}_B_s'];Bt=z[f'case{case}_B_t']
                    rs=np.exp(-gap/(2*(frac*t)**2));rt=np.exp(-gap/(2*t*t));vs=rs@Bs;vt=rt@Bt
                    margins=vs[ind,nn,None]-vt;margins[ind,nn]=np.inf
                    assert np.allclose(margins,z[f'case{case}_margins'],rtol=1e-12,atol=1e-10)
                    rho=np.zeros((10,10))
                    for a in range(10):
                        for b in range(10):
                            if a==b:continue
                            lo=Bs[:,a]-Bt[:,b];hi=Bt[:,a]-Bs[:,b]
                            low=As@np.maximum(lo,0)+At@np.minimum(lo,0)
                            high=At@np.maximum(hi,0)+As@np.minimum(hi,0)
                            rho[a,b]=np.linalg.norm(np.maximum(abs(low),abs(high)))
                    assert np.allclose(rho,z[f'case{case}_rho'],rtol=1e-12,atol=1e-8)
                    for li,mult in enumerate([10,100]):
                        mask=z[f'case{case}_threshold']<=mult*op
                        lhs=margins[mask];rhs=np.linalg.norm(rt[mask],axis=1)[:,None]*rho[nn[mask]]/(mult*op)
                        assert np.all(lhs>rhs)
                        for si,probe in enumerate([.95,.99,1.]):
                            if probe<frac:continue
                            r=np.exp(-gap/(2*(probe*t)**2));W=val[f't{ri}_weights'][li,si];scores=r@W
                            a=scores[ind,nn].copy();scores[ind,nn]=-np.inf;b=scores.max(1)
                            if mask.any():min_margin=min(min_margin,float(np.min((a-b)[mask])))
                            count_disagreements+=int(np.sum((a<=b)&mask));counts['certified_repeated_checks']+=int(mask.sum())
                for li,mult in enumerate([10,100]):
                    for si,frac in enumerate([.95,.99,1.]):
                        case=ci+(0 if frac==.99 else 1)
                        A=At if frac==1 else z[f'case{case}_A_s'];B=z[f'case{ci}_B_t'] if frac==1 else z[f'case{case}_B_s']
                        W=val[f't{ri}_weights'][li,si];res=(A+mult*op*np.eye(100))@W-B
                        relative=float(np.linalg.norm(res)/np.linalg.norm(B));max_resid=max(max_resid,relative);assert relative<1e-12
                        scores=np.exp(-gap/(2*(frac*t)**2))@W;pred=scores.argmax(1)
                        assert np.array_equal(pred,val[f't{ri}_predictions'][li,si]);counts['normal_equation_checks']+=1;counts['reconstructed_prediction_labels']+=n
                        if frac==1:
                            row=next(q for q in all_rows if q['dataset']==ds and int(q['seed'])==seed and float(q['t_over_sC'])==ratio and float(q['lambda_over_At_operator'])==mult)
                            assert abs(float(row['readout_accuracy_pct'])-100*np.mean(pred==truth))<1e-12
                            assert abs(float(row['nearest_agreement_pct'])-100*np.mean(pred==nn))<1e-12
        counts['groups']+=1
assert counts['certified_repeated_checks']==254120
assert count_disagreements==0
report={'status':'PASS',**counts,'strict_certified_score_disagreements':count_disagreements,'minimum_certified_sampled_score_margin':min_margin,'maximum_relative_normal_equation_residual':max_resid}
Path(__file__).with_suffix('.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps(report,indent=2))
