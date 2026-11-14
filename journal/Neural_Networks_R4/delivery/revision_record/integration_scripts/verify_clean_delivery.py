"""Verify freshly extracted R4 source and all delivered numerical evidence."""
from pathlib import Path
import hashlib,json,os,subprocess,time,zipfile
import fitz
ROOT=Path(__file__).resolve().parents[2];CLEAN=ROOT/'tmp/r4_clean';JF=ROOT/'output/RBF_Neural_Networks_R4/journal_files';LOG=ROOT/'logs'
def sha(p):
 h=hashlib.sha256()
 with Path(p).open('rb') as f:
  for b in iter(lambda:f.read(1048576),b''):h.update(b)
 return h.hexdigest()
def js(p,o):p.write_text(json.dumps(o,indent=2)+'\n')
source=CLEAN/'source';m=json.loads((source/'SHA256_MANIFEST.json').read_text())
for n,h in m.items():assert sha(source/n)==h,n
original=fitz.open(ROOT/'working_R4/source/main.pdf');rebuilt=fitz.open(source/'main.pdf')
assert len(original)==len(rebuilt)==41
assert [p.get_text() for p in original]==[p.get_text() for p in rebuilt]
# PDF metadata may differ by build timestamp; page text and rendered pixels must match.
for a,b in zip(original,rebuilt):assert a.get_pixmap().samples==b.get_pixmap().samples
warnings=[x for x in (source/'main.log').read_text().splitlines() if any(k in x for k in ['Overfull','Underfull','undefined','multiply defined'])];assert not warnings
js(LOG/'r4_clean_source_verification.json',{'status':'PASS','source_manifest_files':len(m),'pages':41,'all_page_text_exact':True,'all_rendered_page_pixels_exact':True,'warnings':warnings})
num=CLEAN/'numerics';num.mkdir(exist_ok=True)
with zipfile.ZipFile(JF/'Supplementary_Research_Artifacts_R4.zip') as z:
 assert z.testzip() is None;z.extractall(num)
env=os.environ.copy();env['PYTHONDONTWRITEBYTECODE']='1'
records=[]
commands=[('manifest',['python','verify_package.py'])]+[(stem,['python','r4_analysis/independent/'+script]) for stem,script in [('composition','verify_composition.py'),('competitive','verify_competitive.py'),('paths_efficiency','verify_paths_efficiency.py'),('summary_tables','verify_summary_tables.py')]]
for stem,cmd in commands:
 started=time.perf_counter();log=LOG/f'r4_clean_{stem}.log'
 with log.open('w') as f:subprocess.run(cmd,cwd=num,env=env,stdout=f,stderr=subprocess.STDOUT,check=True)
 if stem=='manifest':result=json.loads(log.read_text())
 else:result=json.loads((num/f'r4_analysis/independent/{stem}_verification.json').read_text())
 assert result['status']=='PASS';records.append({'check':stem,'status':'PASS','elapsed_seconds':time.perf_counter()-started,'log_sha256':sha(log)})
 print(json.dumps(records[-1]),flush=True)
# Original R2 evidence and all delivered R3 analysis bytes remain exactly preserved.
with zipfile.ZipFile(ROOT/'output/RBF_Neural_Networks_R3/journal_files/Supplementary_Research_Artifacts_R3.zip') as z:
 preserved=0
 for name in z.namelist():
  if not name.endswith('/') and name.startswith(('evidence/','r3_analysis/')):
   assert hashlib.sha256(z.read(name)).hexdigest()==sha(num/name),name;preserved+=1
js(LOG/'r4_clean_numerical_verification.json',{'status':'PASS','checks':records,'preserved_R2_R3_files_exact':preserved,'fresh_extraction':True,'new_fits':0})
print('ALL FRESH-EXTRACTION CHECKS PASS',flush=True)
