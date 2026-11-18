"""Create and verify two transport ZIPs that restore the exact full R4 archive."""
from pathlib import Path
import hashlib,json,shutil,subprocess,zipfile
ROOT=Path(__file__).resolve().parents[2];OUT=ROOT/'output';name='RBF_Neural_Networks_Full_Revision_R4_2026-11-14.zip';full=OUT/name;stage=ROOT/'tmp/r4_split';stage.mkdir(exist_ok=True)
def sha(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  for b in iter(lambda:f.read(1048576),b''):h.update(b)
 return h.hexdigest()
parts=[]
with full.open('rb') as f:
 for i in range(2):
  p=stage/(name+f'.part{i+1:03}');p.write_bytes(f.read(354182035));parts.append({'file':p.name,'bytes':p.stat().st_size,'sha256':sha(p)})
 assert not f.read(1)
manifest={'format':'R4 byte-exact split transport v1','archive':name,'bytes':full.stat().st_size,'sha256':sha(full),'parts':parts}
(stage/'RBF_R4_SPLIT_MANIFEST.json').write_text(json.dumps(manifest,indent=2)+'\n')
restore='''#!/usr/bin/env python3
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
'''
(stage/'restore_full_archive.py').write_text(restore)
(stage/'README_RESTORE_R4.txt').write_text('''FULL R4 REVISION PACKAGE — TWO TRANSPORT PARTS

Download both RBF_R4_Archive_Part_1_of_2.zip and RBF_R4_Archive_Part_2_of_2.zip.
Extract both into the same folder (identical README/script/manifest may be kept).
Run from that folder:

    python restore_full_archive.py

This restores RBF_Neural_Networks_Full_Revision_R4_2026-11-14.zip exactly.
The script verifies both part hashes and the complete archive hash before success.
Then unzip the restored archive and follow its README.md.
Python 3 standard library only; no additional dependencies or downloads.
Both transport parts are required. Neither alone is the complete archive.
The standalone manuscript PDF, source ZIP, report, and decision summary are
also supplied separately for immediate reading.
''')
transport=[]
for i,part in enumerate(parts):
 p=OUT/f'RBF_R4_Archive_Part_{i+1}_of_2.zip'
 with zipfile.ZipFile(p,'w',compression=zipfile.ZIP_STORED) as z:
  for n in [part['file'],'restore_full_archive.py','RBF_R4_SPLIT_MANIFEST.json','README_RESTORE_R4.txt']:z.write(stage/n,n)
 transport.append({'path':str(p),'bytes':p.stat().st_size,'sha256':sha(p)})
verify=ROOT/'tmp/r4_split_verification';verify.mkdir(exist_ok=True)
for p in transport:
 with zipfile.ZipFile(p['path']) as z:z.extractall(verify)
r=subprocess.run(['python',str(verify/'restore_full_archive.py')],text=True,capture_output=True,check=True)
assert sha(verify/name)==sha(full)
receipt={'status':'PASS','original_archive':manifest,'transport':transport,'fresh_restoration_exact':True,'restore_output':r.stdout.strip(),'initial_preparation_failure':'Five-file batch including 708 MB archive returned prepare_uploads failed before transfer/finalization; no IDs returned.'}
(ROOT/'logs/r4_split_verification.json').write_text(json.dumps(receipt,indent=2)+'\n')
request=json.loads((ROOT/'tmp/r4_library_request.json').read_text());request['uploads']=request['uploads'][:4]+[{'local_path':p['path'],'purpose':'create_library_file','library_artifact_type':'other'} for p in transport]
(ROOT/'tmp/r4_library_split_request.json').write_text(json.dumps(request,indent=2)+'\n')
print(json.dumps({'status':'PASS','parts':transport,'fresh_restoration_exact':True}))
