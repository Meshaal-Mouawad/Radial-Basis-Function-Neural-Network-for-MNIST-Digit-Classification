"""Uniform nearest-prototype faithfulness certificate; real-arithmetic theorem.
No dataset access. All arrays are float64; production thresholds are explicit.
"""
import numpy as np

METHODS=('sharp','basic','cancellation_frobenius')

def training_terms(H,Y,center_rows):
    K=H.shape[1];H=H.copy();H[center_rows,np.arange(K)]=1.
    E=H.copy();E[center_rows,np.arange(K)]=0.
    Yc=Y[center_rows];Ec=E[center_rows]
    non=np.ones(len(H),bool);non[center_rows]=False
    V=Ec@Yc;P=E[non].T@Y[non];Q=E.T@(E@Yc)
    beta=float(Ec.sum(axis=1).max());mu=max(1-beta,0.)**2
    return {'V':V,'P':P,'Q':Q,'beta':beta,'mu':mu,'eta':float(np.linalg.norm(E)),
            'Yc':Yc,'training_class_counts':Y.sum(axis=0),'prototype_class_counts':Yc.sum(axis=0)}

def constants(terms,lambda0):
    V,P,Q=terms['V'],terms['P'],terms['Q'];classes=V.shape[1]
    den=terms['mu']+lambda0
    result=np.full((3,classes,classes),np.inf)
    if den<=0:return result,False
    for a in range(classes):
        for b in range(classes):
            if a==b:result[:,a,b]=0.;continue
            v,p,q=V[:,a]+V[:,b],P[:,a]+P[:,b],Q[:,a]+Q[:,b]
            at0=(abs(lambda0-1)*v+(lambda0+1)*p+q)/den
            result[0,a,b]=max(np.linalg.norm(at0),np.linalg.norm(v+p))
            result[1,a,b]=np.linalg.norm(((lambda0+1)*(v+p)+q)/den)
            eta=terms['eta'];n=terms['training_class_counts'];k=terms['prototype_class_counts']
            result[2,a,b]=((1+lambda0)*eta*np.sqrt(n[a]+n[b])+(eta*eta)*np.sqrt(k[a]+k[b]))/den
    tol=1e-10*(1+np.abs(result[2]))
    assert np.all(result[0]<=result[1]+tol)
    assert np.all(result[1]<=result[2]+tol)
    return result,True

def query_features(D,sigma):
    return np.exp(-(D-D.min(axis=1,keepdims=True))/(2*sigma*sigma))

def query_certificate(D,Yc,t,bounds,guard=1e-10,tie_relative=1e-12):
    nearest=np.argmin(D,axis=1);ref=np.argmax(Yc[nearest],axis=1)
    r=query_features(D,t);classmass=r@Yc;norm=np.linalg.norm(r,axis=1)
    smallest=np.partition(D,1,axis=1)[:,:2]
    unique=smallest[:,1]-smallest[:,0]>tie_relative*np.maximum(1.,np.max(smallest,axis=1))
    lhs=1-classmass;cert=np.zeros((3,len(D)),bool);minimum_gaps=np.full((3,len(D)),-np.inf)
    for m in range(3):
        rhs=norm[:,None]*bounds[m,ref,:]
        gap=lhs-rhs;tol=guard*(1+np.abs(lhs)+np.abs(rhs))
        success=(gap>tol);success[np.arange(len(D)),ref]=True
        gap[np.arange(len(D)),ref]=np.inf
        cert[m]=unique&success.all(axis=1)
        minimum_gaps[m]=gap.min(axis=1)
    return cert,ref,minimum_gaps,unique
