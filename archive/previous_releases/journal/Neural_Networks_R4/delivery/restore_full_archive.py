#!/usr/bin/env python3
"""Reassemble the original complete R4 ZIP after extracting both transport ZIPs."""
from pathlib import Path
import hashlib,json,sys
root=Path(__file__).resolve().parent
m=json.loads((root/'RBF_R4_SPLIT_MANIFEST.json').read_text())
def digest(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  for b in iter(lambda:f.read(1048576),b''):h.update(b)
 return h.hexdigest()
output=root/m['archive']
if output.exists():
 if output.stat().st_size==m['bytes'] and digest(output)==m['sha256']:
  print('PASS: the full archive already exists with the exact expected hash.');sys.exit(0)
 raise SystemExit('Refusing to overwrite a different existing archive.')
for part in m['parts']:
 p=root/part['file']
 assert p.is_file(),f'Missing part: {p.name}. Extract both transport ZIPs into this folder.'
 assert p.stat().st_size==part['bytes'] and digest(p)==part['sha256'],f'Part hash mismatch: {p.name}'
temp=output.with_suffix(output.suffix+'.assembling')
with temp.open('wb') as target:
 for part in m['parts']:
  with (root/part['file']).open('rb') as source:
   for block in iter(lambda:source.read(1048576),b''):target.write(block)
assert temp.stat().st_size==m['bytes'] and digest(temp)==m['sha256'],'Reassembled archive hash mismatch'
temp.rename(output)
print('PASS: reconstructed '+output.name+'; '+str(m['bytes'])+' bytes; SHA-256 '+m['sha256'])
