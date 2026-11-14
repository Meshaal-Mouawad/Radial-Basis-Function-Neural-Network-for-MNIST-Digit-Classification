"""Freeze R4 after independent reviews and fresh-extraction verification."""
from pathlib import Path
import hashlib,json,re,shutil,zipfile
ROOT=Path(__file__).resolve().parents[2];PKG=ROOT/'output/RBF_Neural_Networks_R4';REC=PKG/'revision_record';JF=PKG/'journal_files'
def sha(p):
 h=hashlib.sha256()
 with Path(p).open('rb') as f:
  for b in iter(lambda:f.read(1048576),b''):h.update(b)
 return h.hexdigest()
def js(p,o):Path(p).write_text(json.dumps(o,indent=2)+'\n')
checks={}
for n in ['r4_clean_source_verification.json','r4_clean_numerical_verification.json']:
 checks[n]=json.loads((ROOT/'logs'/n).read_text());assert checks[n]['status']=='PASS';shutil.copy2(ROOT/'logs'/n,REC/n)
for p in (ROOT/'logs').glob('r4_clean_*.log'):shutil.copy2(p,REC/p.name)
for p in (ROOT/'r4_analysis/integration').glob('*.py'):shutil.copy2(p,REC/'integration_scripts'/p.name)
for p in (ROOT/'r4_analysis/review').iterdir():
 if p.is_file() and p.suffix in ['.md','.json']:shutil.copy2(p,REC/p.name)
# The separate reviewer supplies a final read-only source check.
independent=ROOT/'r4_analysis/review/independent_source_consistency.md'
assert independent.exists(),'Awaiting final independent source consistency review'
text=independent.read_text();assert re.search(r'^Status:\s*\*?\*?PASS\b',text,re.M) and 'PARTIAL' not in text and 'FAIL' not in text,text
source_audit=json.loads(independent.with_suffix('.json').read_text());assert source_audit['status']=='PASS'
for name,value in source_audit['source_files_sha256'].items():assert sha(ROOT/name)==value,name
remote=json.loads((ROOT/'r4_analysis/github_preservation.json').read_text());assert remote['status']=='PASS';shutil.copy2(ROOT/'r4_analysis/github_preservation.json',REC/'GITHUB_PRESERVATION.json')
checks['document_visual_inspection']='All three report pages, one decision-summary page and one cover-letter page inspected; no overflow or clipping.'
checks['status']='PASS';js(REC/'FINAL_DELIVERY_VERIFICATION.json',checks)
ready={'status':'REVIEW_READY','internal_author_review':True,'journal_significance_resolved':False,'journal_transfer_submission_complete':False,'new_fits':0,'gates':{'C_composition':'PASS','D_finite_paths':'PASS','E_competitive_regimes':'PASS','F_probe_accumulation':'PASS','G_seed_stability':'PASS','independent_numerical_reconstruction':'PASS','independent_source_consistency':'PASS','original_protection':'PASS','R3_checkpoint_unchanged':'PASS','latex_compilation':'PASS','all_41_pdf_pages_inspected':'PASS','fresh_source_compilation_exact_pixels':'PASS','fresh_supplement_four_verifiers':'PASS','complete_archived_evidence_preserved':'PASS','github_recorded_scope_exact':'PASS'},'delivery_hashes':{p.name:sha(p) for p in JF.iterdir() if p.name in ['RBF_Neural_Networks_Manuscript_R4.pdf','LaTeX_Source_Neural_Networks_R4.zip','Supplementary_Research_Artifacts_R4.zip']},'source_review_sha256':sha(independent),'github_receipt_sha256':sha(REC/'GITHUB_PRESERVATION.json'),'scope':'All approved saved-evidence analyses and manuscript production complete. The editor\'s significance assessment remains open.'}
js(REC/'REVIEW_READY.json',ready);js(ROOT/'r4_analysis/REVIEW_READY.json',ready)
manifest={str(p.relative_to(PKG)):sha(p) for p in sorted(PKG.rglob('*')) if p.is_file() and p!=PKG/'SHA256_MANIFEST.json'};js(PKG/'SHA256_MANIFEST.json',manifest)
out=ROOT/'output/RBF_Neural_Networks_Full_Revision_R4_2026-11-14.zip'
with zipfile.ZipFile(out,'w') as z:
 for p in sorted(PKG.rglob('*')):
  if p.is_file():z.write(p,PKG.name+'/'+str(p.relative_to(PKG)),compress_type=zipfile.ZIP_STORED if p.suffix=='.zip' else zipfile.ZIP_DEFLATED,compresslevel=6)
with zipfile.ZipFile(out) as z:
 assert z.testzip() is None
 for n,h in manifest.items():
  hh=hashlib.sha256()
  with z.open(PKG.name+'/'+n) as f:
   for b in iter(lambda:f.read(1048576),b''):hh.update(b)
  assert hh.hexdigest()==h,n
receipt={'status':'PASS','files':len(manifest)+1,'bytes':out.stat().st_size,'sha256':sha(out),'full_archive':str(out),'ready_gate':str(REC/'REVIEW_READY.json')};js(ROOT/'logs/r4_final_archive.json',receipt);print(json.dumps(receipt),flush=True)
