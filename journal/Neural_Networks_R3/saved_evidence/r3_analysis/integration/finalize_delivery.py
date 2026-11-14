"""Record fresh-extraction verification and finalize the R3 delivery archive."""
import hashlib,json,shutil,zipfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
PKG=ROOT/'output/RBF_Neural_Networks_R3'
REC=PKG/'revision_record'
def digest(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  for b in iter(lambda:f.read(1048576),b''):h.update(b)
 return h.hexdigest()
checks={}
for name in ['r3_packaged_source_match.json','r3_archive_verification.json','r3_packaged_m1_m2.log','r3_packaged_m3.log','r3_packaged_r2.log']:
 p=ROOT/'logs'/name
 checks[name]=json.loads(p.read_text());assert checks[name]['status']=='PASS'
 shutil.copy2(p,REC/name)
independent=json.loads((ROOT/'tmp/packaged_check/numerics/r3_analysis/independent/verification.json').read_text())
assert independent['status']=='PASS';checks['fresh_extraction_independent']=independent
checks['status']='PASS'
checks['report_and_cover_pdf_visual_check']='Four report pages and one cover-letter page inspected; no clipping or layout defects.'
(REC/'FINAL_DELIVERY_VERIFICATION.json').write_text(json.dumps(checks,indent=2)+'\n')
shutil.copy2(ROOT/'logs/r3_packaged_source_build.log',REC/'r3_packaged_source_build.log')
shutil.copy2(Path(__file__),REC/'integration_scripts/finalize_delivery.py')
manifest={str(p.relative_to(PKG)):digest(p) for p in sorted(PKG.rglob('*')) if p.is_file() and p!=PKG/'SHA256_MANIFEST.json'}
(PKG/'SHA256_MANIFEST.json').write_text(json.dumps(manifest,indent=2)+'\n')
out=ROOT/'output/RBF_Neural_Networks_Full_Revision_R3_2026-11-14.zip'
with zipfile.ZipFile(out,'w',zipfile.ZIP_DEFLATED,compresslevel=6) as z:
 for p in sorted(PKG.rglob('*')):
  if p.is_file():z.write(p,PKG.name+'/'+str(p.relative_to(PKG)))
with zipfile.ZipFile(out) as z:
 assert z.testzip() is None
 m=json.loads(z.read(PKG.name+'/SHA256_MANIFEST.json'))
 for name,value in m.items():assert hashlib.sha256(z.read(PKG.name+'/'+name)).hexdigest()==value,name
print(json.dumps({'status':'PASS','zip_entries':len(manifest)+1,'bytes':out.stat().st_size,'sha256':digest(out)}))
