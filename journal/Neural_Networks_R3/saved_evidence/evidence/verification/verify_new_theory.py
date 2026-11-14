"""Independent synthetic checks for proposed additions; original artifacts untouched."""
import json
from fractions import Fraction as F
from pathlib import Path
import numpy as np

rng=np.random.default_rng(20261109)
counts=dict(datasets=0, interval_enclosures=0, certified_bands=0, certified_predictions=0, resolvent_checks=0, strict_obstruction_checks=0)
max_error=0.0
for case in range(250):
    N,K,C=24,6,3
    X=rng.normal(size=(N,2)); P=X[:K]
    labels=rng.integers(C,size=N); Y=np.eye(C)[labels]
    Q=rng.normal(size=(12,2))
    D=((X[:,None,:]-P[None,:,:])**2).sum(2)
    Dq=((Q[:,None,:]-P[None,:,:])**2).sum(2)
    nearest=Dq.argmin(1); targets=labels[nearest]
    gaps=Dq-Dq.min(1,keepdims=True)
    t=float(np.exp(rng.uniform(-2.8,.6))); s=t*float(rng.choice([.95,.99]))
    Hs=np.exp(-D/(2*s*s)); Ht=np.exp(-D/(2*t*t))
    Bs=Hs.T@Y; Bt=Ht.T@Y; As=Hs.T@Hs; At=Ht.T@Ht
    rs=np.exp(-gaps/(2*s*s)); rt=np.exp(-gaps/(2*t*t))
    vs=rs@Bs; vt=rt@Bt
    rho=np.zeros((C,C))
    for a in range(C):
        for b in range(C):
            lo=Bs[:,a]-Bt[:,b]; hi=Bt[:,a]-Bs[:,b]
            zl=As@np.maximum(lo,0)+At@np.minimum(lo,0)
            zu=At@np.maximum(hi,0)+As@np.minimum(hi,0)
            rho[a,b]=np.linalg.norm(np.maximum(abs(zl),abs(zu)))
            for sig in np.linspace(s,t,7):
                H=np.exp(-D/(2*sig*sig)); A=H.T@H; B=H.T@Y
                z=A@(B[:,a]-B[:,b])
                assert np.all(z>=zl-1e-11) and np.all(z<=zu+1e-11)
                counts['interval_enclosures']+=1
    for i,a in enumerate(targets):
        rivals=[b for b in range(C) if b!=a]
        margins=np.array([vs[i,a]-vt[i,b] for b in rivals])
        if min(margins)>1e-9:
            L=max(np.linalg.norm(rt[i])*rho[a,b]/m for b,m in zip(rivals,margins))
            L=max(1e-6,1.01*L)
            counts['certified_bands']+=1
            for sig in np.linspace(s,t,5):
                H=np.exp(-D/(2*sig*sig)); A=H.T@H; B=H.T@Y
                r=np.exp(-gaps[i]/(2*sig*sig))
                for lam in [L,10*L,100*L]:
                    scores=r@np.linalg.solve(np.eye(K)+A/lam,B)
                    assert all(scores[a]>scores[b] for b in rivals)
                    counts['certified_predictions']+=1
        # Fixed-width resolvent bound for arbitrary query and class pair.
        v=Bt[:,0]-Bt[:,1]; delta=rt[i]@v
        lam=float(np.exp(rng.uniform(-5,10)))
        score=rt[i]@np.linalg.solve(np.eye(K)+At/lam,v)
        error=abs(score-delta)
        bound=np.linalg.norm(rt[i])*np.linalg.norm(At@v)/lam
        assert error<=bound+1e-10
        counts['resolvent_checks']+=1
        max_error=max(max_error,float(error/(bound+1e-300)))
        if abs(delta)>1e-9:
            threshold=np.linalg.norm(rt[i])*np.linalg.norm(At@v)/abs(delta)
            lam=max(1e-8,1.01*threshold)
            score=rt[i]@np.linalg.solve(np.eye(K)+At/lam,v)
            assert delta*score>0
            counts['strict_obstruction_checks']+=1
    counts['datasets']+=1

# Exact finite-Gaussian examples: distance d=sqrt(2 log 2), sigma=1,
# giving selected-prototype cross-response q=1/2. Query is prototype 0.
q=F(1,2)
# Three observations: coordinates 0,d,0 and labels a,b,b.
# A=[[9/4,3/2],[3/2,3/2]], v=B_b-B_a=[1/2,1].
A=[[F(9,4),F(3,2)],[F(3,2),F(3,2)]]; v=[q,F(1)]
def numerator(A,v,lam):
    return (A[1][1]+lam)*v[0]-A[0][1]*v[1]+q*(-A[1][0]*v[0]+(A[0][0]+lam)*v[1])
assert v[0]+q*v[1]==1
for lam in [F(0),F(1,10),F(1),F(10),F(100)]:
    assert numerator(A,v,lam)==lam
# Exact tied asymptote with finite a winner: 5a+1b at 0, 1a+6b at d.
# Select one a at 0 and one b at d as prototypes.
Atie=[[F(31,4),F(13,2)],[F(13,2),F(17,2)]]; vtie=[F(-3,2),F(3)]
assert vtie[0]+q*vtie[1]==0
for lam in [F(0),F(1,10),F(1),F(10),F(100)]:
    assert numerator(Atie,vtie,lam)==F(-63,4)
result={'seed':20261109,**counts,'violations':0,'max_observed_resolvent_error_to_bound_ratio':max_error,
        'exact_gaussian_obstruction':'r^T(W_b-W_a)=lambda/det(A+lambda I), positive for every lambda>0',
        'exact_tied_limit':'r^T(W_b-W_a)=(-63/4)/det(A+lambda I), negative for every lambda>=0 despite limit tie'}
Path(__file__).with_suffix('.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps(result,indent=2))
