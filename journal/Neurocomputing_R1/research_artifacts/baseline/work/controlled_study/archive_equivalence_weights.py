#!/usr/bin/env python3
"""Reconstruct already fixed equivalence checks to archive both fitted weights.

This auxiliary audit changes no protocol, model selection, or original result.
It uses saved split and center indices and confirms the archived scalar metrics.
"""
import csv
import json
from datetime import datetime,timezone
from pathlib import Path

import numpy as np
from scipy.io import loadmat
from scipy.spatial.distance import cdist
from threadpoolctl import threadpool_limits

from run_study import factor,flatten,rls,sha256,solve_from_factor,write_json

ROOT=Path(__file__).resolve().parent
DATA=ROOT.parents[1]/'repository'/'Code'
R=ROOT/'results'
A=R/'equivalence_weights'
A.mkdir(exist_ok=True)
env=json.loads((R/'environment.json').read_text())
assert sha256(ROOT/'run_study.py')==env['source_sha256']
for name,h in env['data_sha256'].items():
    assert sha256(DATA/name)==h
with (R/'rls_equivalence.csv').open() as f:
    rows=list(csv.DictReader(f))
train=loadmat(DATA/'MNIST_train.mat')
test=loadmat(DATA/'MNIST_test.mat')
images=train['imagestrain']; labels=train['labelstrain'].ravel().astype(int)
test_images=test['images']
records=[]
with threadpool_limits(limits=1):
    for seed in [11,22,33,44,55]:
        z=np.load(R/f'seed_{seed}_predictions.npz')
        X=flatten(images,z['train_ids'])
        C=flatten(images,z['center_ids'])
        XT=flatten(test_images,z['test_ids'])
        Y=np.eye(10)[labels[z['train_ids']]]
        D=cdist(X,C,'sqeuclidean');DT=cdist(XT,C,'sqeuclidean')
        saved={'train_ids':z['train_ids'],'center_ids':z['center_ids'],'test_ids':z['test_ids'],'test_y':z['test_y']}
        cached={}
        for i,row in enumerate(r for r in rows if int(r['seed'])==seed):
            sigma=float(row['sigma']);lam=float(row['lambda']);name=row['width']
            if name not in cached:
                H=np.exp(-D/(2*sigma*sigma));HT=np.exp(-DT/(2*sigma*sigma))
                s,vt,uty,_=factor(H,Y)
                cached[name]=(H,HT,s,vt,uty)
            H,HT,s,vt,uty=cached[name]
            Wb,_=solve_from_factor(s,vt,uty,lam,len(X))
            Wr,_=rls(H,Y,lam)
            pb=np.argmax(HT@Wb,axis=1);pr=np.argmax(HT@Wr,axis=1)
            relative=float(np.linalg.norm(Wr-Wb)/np.linalg.norm(Wb))
            maximum=float(np.max(np.abs(HT@Wb-HT@Wr)))
            assert np.array_equal(pb,pr)
            assert np.isclose(relative,float(row['relative_weight_error']),rtol=1e-6,atol=1e-15)
            assert np.isclose(maximum,float(row['max_absolute_test_score_error']),rtol=1e-6,atol=1e-14)
            key=f'check_{i}'
            saved[key+'_batch_W']=Wb;saved[key+'_rls_W']=Wr
            saved[key+'_batch_prediction']=pb;saved[key+'_rls_prediction']=pr
            records.append({'seed':seed,'key':key,'width':name,'sigma':sigma,'lambda':lam,
                            'relative_weight_error':relative,'maximum_score_error':maximum,
                            'prediction_disagreements':int(np.sum(pb!=pr)),'matches_original_record':True})
        np.savez_compressed(A/f'seed_{seed}_weights.npz',**saved)
        print('archived',seed,flush=True)
write_json(A/'AUDIT.json',{'completed_at_utc':datetime.now(timezone.utc).isoformat(),
                         'purpose':'additional archive of both weights and predictions for the existing 35 equivalence conditions',
                         'original_source_sha256':env['source_sha256'],'auxiliary_source_sha256':sha256(__file__),
                         'scientific_protocol_unchanged':True,'records':records})
