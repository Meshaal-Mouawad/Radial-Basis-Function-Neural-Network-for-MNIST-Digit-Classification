"""Independent synthetic audit of the finite-width / penalty rectangle certificate.
No experiment datasets are read. This file evaluates only generated geometries.
"""
from pathlib import Path
import json, hashlib, numpy as np

RNG=np.random.default_rng(6700611)
OUT=Path(__file__).resolve().parent

def features(X,C,sigma):
    d=np.sum((X[:,None,:]-C[None,:,:])**2,axis=2)
    return np.exp(-d/(2*sigma*sigma))

def bound(X,y,ids,q,t,l0,Cn):
    centers=X[ids]
    H=features(X,centers,t)
    S=np.zeros_like(H);S[ids,np.arange(len(ids))]=1
    E=H-S;Y=np.eye(Cn)[y];Yc=Y[ids]
    Ec=E[ids]
    rem=np.ones(len(X),bool);rem[ids]=False
    V=Ec@Yc;P=E[rem].T@Y[rem];Q=E.T@(E@Yc)
    beta=np.max(np.sum(Ec,axis=1));c=max(1-beta,0)**2
    denom=c+l0
    d=np.sum((q[:,None,:]-centers[None,:,:])**2,axis=2)
    nearest=np.argmin(d,axis=1);cl=y[ids][nearest]
    rr=np.exp(-(d-d.min(axis=1,keepdims=True))/(2*t*t))
    nr=np.linalg.norm(rr,axis=1)
    margins=np.zeros((len(q),Cn));Ds=np.full((Cn,Cn),np.inf);Db=Ds.copy()
    if denom>0:
        for a in range(Cn):
            for b in range(Cn):
                if a==b: continue
                vp=V[:,a]+V[:,b];pp=P[:,a]+P[:,b];qp=Q[:,a]+Q[:,b]
                Ds[a,b]=max(np.linalg.norm((abs(l0-1)*vp+(1+l0)*pp+qp)/denom),np.linalg.norm(vp+pp))
                Db[a,b]=np.linalg.norm(((1+l0)*(vp+pp)+qp)/denom)
        assert np.all(Ds[np.isfinite(Ds)]<=Db[np.isfinite(Db)]+1e-12)
    cert=np.ones(len(q),bool)
    for i,a in enumerate(cl):
        for b in range(Cn):
            if a==b: continue
            margins[i,b]=1-rr[i,y[ids]==b].sum()-nr[i]*Ds[a,b]
            cert[i] &= margins[i,b]>1e-12
    return cert,cl,dict(H=H,S=S,E=E,Y=Y,Yc=Yc,V=V,P=P,Q=Q,beta=beta,c=c,Ds=Ds,Db=Db,margin=margins)

cases=[]; checks=0; certified_queries=0; certified_checks=0; violations=[]
residual_error=0.; uniform_excess=0.; bound_count=0; sharp_strict=0
widths=[.025,.08,.2,.5,1.5]
for trial in range(60):
    n=int(RNG.integers(7,22));k=int(RNG.integers(2,min(7,n)));dim=int(RNG.integers(1,5));classes=int(RNG.integers(2,5))
    X=RNG.normal(size=(n,dim));y=RNG.integers(classes,size=n);ids=RNG.choice(n,k,False)
    # Include near-prototype queries to exercise nonempty certified regions.
    q=np.concatenate([X[ids]+RNG.normal(scale=.005,size=(k,dim)),RNG.normal(size=(5,dim))])
    for t in widths:
      for l0 in [0.,.1,1.,10.]:
        cert,nn,z=bound(X,y,ids,q,t,l0,classes)
        certified_queries+=int(cert.sum())
        finite=np.isfinite(z['Ds']);finite &= ~np.eye(classes,dtype=bool)
        sharp_strict+=int(np.sum(z['Ds'][finite]<z['Db'][finite]-1e-12));bound_count+=int(finite.sum())
        for sf in [.01,.1,.5,.9,1.]:
          s=t*sf;H=features(X,X[ids],s);E=H-z['S']
          for lam in sorted(set([l0,l0+.01,max(1.,l0),l0+10.,1e8])):
            aa=1+lam;G=H.T@H+lam*np.eye(k)
            # Solve for (1+lambda)W, which has identical decisions and is stable at large lambda.
            try: aW=np.linalg.solve(G/aa,H.T@z['Y'])
            except np.linalg.LinAlgError:
                assert not cert.any(); continue
            d=np.sum((q[:,None,:]-X[ids][None,:,:])**2,axis=2)
            h=np.exp(-(d-d.min(axis=1,keepdims=True))/(2*s*s))
            pred=np.argmax(h@aW,axis=1)
            bad=np.flatnonzero(cert & (pred!=nn));checks+=len(q);certified_checks+=int(cert.sum())
            if len(bad):violations.append({'trial':trial,'t':t,'lambda0':l0,'sigma':s,'lambda':lam,'queries':bad.tolist()})
            Yc=z['Yc'];Ec=E[ids];rem=np.ones(n,bool);rem[ids]=False
            V=Ec@Yc;P=E[rem].T@z['Y'][rem];Q=E.T@(E@Yc)
            exact=H.T@z['Y']-G@Yc/aa
            decomposed=((lam-1)/aa)*V+P-Q/aa
            residual_error=max(residual_error,float(np.max(np.abs(exact-decomposed))))
            if z['c']+l0>0:
              for a in range(classes):
                for b in range(classes):
                  if a==b:continue
                  actual=np.linalg.norm(aW[:,a]-aW[:,b]-(Yc[:,a]-Yc[:,b]))
                  # Upper bound is independent of both sigma and lambda.
                  uniform_excess=max(uniform_excess,float(actual-z['Ds'][a,b]))
        cases.append({'trial':trial,'width_upper':t,'lambda_lower':l0,'query_count':len(q),'certified':int(cert.sum())})

# Explicit edge cases; an opposite-class nearest tie cannot pass the strict margin.
edge=[]
for tag,X,y,ids,q,t,l0,cls in [
 ('opposite_class_tie',np.array([[-1.],[1.],[3.]]),np.array([0,1,1]),np.array([0,1]),np.array([[0.]]),.05,0.,2),
 ('same_class_tie',np.array([[-1.],[1.],[3.]]),np.array([0,0,1]),np.array([0,1]),np.array([[0.]]),.05,0.,2),
 ('absent_prototype_class',np.array([[-1.],[1.],[3.]]),np.array([0,0,1]),np.array([0,1]),np.array([[-1.01]]),.05,0.,2),
 ('duplicate_centers_positive_lambda',np.array([[0.],[0.],[3.]]),np.array([0,0,1]),np.array([0,1]),np.array([[.01]]),.05,1.,2),
 ('duplicate_centers_zero_lambda',np.array([[0.],[0.],[3.]]),np.array([0,0,1]),np.array([0,1]),np.array([[.01]]),.05,0.,2),
]:
 c,p,z=bound(X,y,ids,q,t,l0,cls)
 edge.append({'case':tag,'certified':c.tolist(),'nearest_class':p.tolist(),'beta':float(z['beta']),'denominator':float(z['c']+l0)})

result={'audit':'synthetic only; no MNIST/Fashion arrays read','random_seed':6700611,'generated_geometries':60,'endpoint_conditions':len(cases),'query_evaluations':checks,'certified_endpoint_queries':certified_queries,'certified_query_parameter_checks':certified_checks,'violations':violations,'max_residual_identity_abs_error':residual_error,'max_weight_bound_excess':uniform_excess,'pair_bounds_compared':bound_count,'strictly_smaller_sharp_pair_bounds':sharp_strict,'edge_cases':edge,'source_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest()}
(OUT/'synthetic_audit.json').write_text(json.dumps(result,indent=2)+'\n')
assert not violations
assert residual_error<1e-12
assert uniform_excess<1e-8
print(json.dumps(result,indent=2))
