#!/usr/bin/env python3
"""Restore all original R2 and R3 evidence from this GitHub checkout."""
import argparse,hashlib,json
from pathlib import Path
p=argparse.ArgumentParser();p.add_argument('--destination',type=Path,required=True);a=p.parse_args()
here=Path(__file__).resolve().parent
repo=next(x for x in here.parents if (x/'.git').exists())
entries=json.loads((here/'RESTORE_MANIFEST.json').read_text())
a.destination.mkdir(parents=True,exist_ok=True)
for e in entries:
 target=a.destination/e['path'];target.parent.mkdir(parents=True,exist_ok=True)
 h=hashlib.sha256();size=0
 with target.open('wb') as out:
  for source in e['sources']:
   with (repo/source).open('rb') as f:
    for data in iter(lambda:f.read(1048576),b''):
     h.update(data);size+=len(data);out.write(data)
 assert size==e['bytes'],e['path']
 assert h.hexdigest()==e['sha256'],e['path']
print(json.dumps({'status':'PASS','restored_files':len(entries),'bytes':sum(e['bytes'] for e in entries)}))
