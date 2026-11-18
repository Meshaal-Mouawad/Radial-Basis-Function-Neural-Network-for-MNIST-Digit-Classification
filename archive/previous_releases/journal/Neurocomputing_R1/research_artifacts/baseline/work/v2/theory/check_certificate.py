"""Synthetic verification only. No MNIST data or held-out study files read."""
from pathlib import Path
import json
import numpy as np
from scipy.spatial.distance import cdist


def prepare(X, y, center_rows, t, lam0, classes):
    C=X[center_rows];Y=np.eye(classes)[y];Yc=Y[center_rows]
    H=np.exp(-cdist(X,C,'sqeuclidean')/(2*t*t))
    H[center_rows,np.arange(len(C))]=1.
    E=H.copy();E[center_rows,np.arange(len(C))]-=1.
    Ec=E[center_rows]
    non=np.ones(len(X),bool);non[center_rows]=False
    V=Ec@Yc;P=E[non].T@Y[non];Q=E.T@(E@Yc)
    beta=np.max(np.sum(Ec,axis=1));c=max(1-beta,0.)**2
    B=np.full((classes,classes),np.inf)
    if c+lam0>0:
        for a in range(classes):
            for b in range(classes):
                if a==b: B[a,b]=0.;continue
                v=V[:,a]+V[:,b];p=P[:,a]+P[:,b];q=Q[:,a]+Q[:,b]
                at0=(abs(lam0-1)*v+(lam0+1)*p+q)/(c+lam0)
                atinfty=v+p
                B[a,b]=max(np.linalg.norm(at0),np.linalg.norm(atinfty))
    return {'V':V,'P':P,'Q':Q,'beta':beta,'c':c,'bounds':B,'Yc':Yc,'H':H}


def certify(Z,C,yc,t,terms):
    D=cdist(Z,C,'sqeuclidean');nearest=np.argmin(D,axis=1);a=yc[nearest]
    r=np.exp(-(D-D[np.arange(len(D)),nearest,None])/(2*t*t))
    classmass=r@terms['Yc'];norm=np.linalg.norm(r,axis=1)
    gaps=1-classmass-norm[:,None]*terms['bounds'][a]
    gaps[np.arange(len(D)),a]=np.inf
    unique=np.sum(D==D[np.arange(len(D)),nearest,None],axis=1)==1
    return unique & np.all(gaps>1e-12,axis=1),a,gaps


def check():
    rng=np.random.default_rng(983127);counts={'synthetic_datasets':0,'query_rectangle_checks':0,'certified_query_rectangles':0,'fitted_comparisons':0,'certified_label_violations':0,'residual_bound_failures':0,'eigenvalue_bound_failures':0,'loose_dominance_failures':0};worst_residual=-np.inf;worst_eig=-np.inf
    for trial in range(100):
        K=int(rng.integers(3,12));N=int(rng.integers(K+2,80));d=int(rng.integers(2,7));L=4
        X=rng.normal(size=(N,d))*rng.uniform(.5,3);y=rng.integers(L,size=N);idx=rng.choice(N,K,False);C=X[idx];Y=np.eye(L)[y];Yc=Y[idx]
        t=float(rng.choice([.05,.15,.35,.7,1.5]));Z=np.vstack([C+rng.normal(scale=.01,size=C.shape),rng.normal(size=(15,d))*2])
        for lam0 in [0.,1.,100.]:
            q=prepare(X,y,idx,t,lam0,L);cert,a,gaps=certify(Z,C,y[idx],t,q);counts['query_rectangle_checks']+=len(Z);counts['certified_query_rectangles']+=int(cert.sum())
            if q['c']+lam0>0:
                for aa in range(L):
                    for bb in range(L):
                        v=q['V'][:,aa]+q['V'][:,bb];p=q['P'][:,aa]+q['P'][:,bb];qq=q['Q'][:,aa]+q['Q'][:,bb]
                        loose=np.linalg.norm(((1+lam0)*(v+p)+qq)/(q['c']+lam0))
                        if q['bounds'][aa,bb]>loose+1e-9:counts['loose_dominance_failures']+=1
            for sig in [t*.01,t*.25,t*.5,t*.75,t]:
                H=np.exp(-cdist(X,C,'sqeuclidean')/(2*sig*sig));H[idx,np.arange(K)]=1.;Dq=cdist(Z,C,'sqeuclidean');hq=np.exp(-(Dq-Dq.min(axis=1,keepdims=True))/(2*sig*sig))
                for lam in [lam0,lam0+.1,lam0+1,lam0+10,lam0+1000]:
                    G=H.T@H+lam*np.eye(K);vmin=np.linalg.eigvalsh(G)[0];lb=q['c']+lam
                    worst_eig=max(worst_eig,lb-vmin)
                    if vmin+1e-8<lb:counts['eigenvalue_bound_failures']+=1
                    if vmin<=1e-12:continue
                    W=np.linalg.solve(G,H.T@Y);pred=np.argmax(hq@W,axis=1);counts['fitted_comparisons']+=len(Z);counts['certified_label_violations']+=int(np.sum(cert&(pred!=a)))
                    resid=H.T@Y-G@(Yc/(1+lam));u=(abs(lam-1)*q['V']+(lam+1)*q['P']+q['Q'])/(1+lam)
                    over=np.max(np.abs(resid)-u);worst_residual=max(worst_residual,float(over))
                    if over>1e-8:counts['residual_bound_failures']+=1
        counts['synthetic_datasets']+=1
    counts['worst_residual_excess']=worst_residual;counts['worst_lower_eigenvalue_excess']=worst_eig
    assert counts['certified_label_violations']==counts['residual_bound_failures']==counts['eigenvalue_bound_failures']==counts['loose_dominance_failures']==0,counts
    # Counterexample to unconditional prototype-label limit with contradictory duplicate.
    X=np.array([[0.],[0.],[0.],[3.]]); y=np.array([0,1,1,1]);idx=np.array([0,3]);H=np.exp(-cdist(X,X[idx],'sqeuclidean')/(2*.01**2));W=np.linalg.solve(H.T@H+np.eye(2),H.T@np.eye(2)[y]);pred=int(np.argmax(np.array([[1.,0.]])@W));assert pred==1
    counts['contradictory_duplicate_counterexample']={'nearest_selected_prototype_label':0,'small_width_ridge_prediction':pred,'matrix_W':W.tolist()}
    p=Path(__file__).with_name('synthetic_verification.json');p.write_text(json.dumps(counts,indent=2)+'\n');print(json.dumps(counts,indent=2))

if __name__=='__main__':check()
