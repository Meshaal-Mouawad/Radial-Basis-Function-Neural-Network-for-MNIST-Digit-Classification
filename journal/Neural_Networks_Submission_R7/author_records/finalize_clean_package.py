from pathlib import Path
import json,zipfile,hashlib,subprocess
R=Path(__file__).resolve().parents[1];P=R/'submission_clean';U=P/'journal_upload';A=P/'author_records';O=R/'output';sha=lambda b:hashlib.sha256(b).hexdigest()
assert json.loads((A/'FINAL_CLEAN_CHECK.json').read_text())['status']=='PASS'
files={str(p.relative_to(U)):p.read_bytes() for p in sorted(U.rglob('*')) if p.is_file()}
small=O/'Neural_Networks_R7_Clean_Upload_Files.zip'
with zipfile.ZipFile(small,'w',zipfile.ZIP_DEFLATED) as z:
 for n,b in files.items():z.writestr(n,b)
supp=R/'restored/full_R5/RBF_Neural_Networks_R5/journal_files/Supplementary_Research_Artifacts_R4.zip';assert sha(supp.read_bytes())=='ee029862791413b993387234efe9ecad5114d99685ef5fd9d4add4eb53d080c8'
full=O/'Neural_Networks_R7_Clean_Submission_Package.zip'
with zipfile.ZipFile(full,'w',zipfile.ZIP_DEFLATED) as z:
 for n,b in files.items():z.writestr(n,b)
 z.write(supp,'Supplementary_Research_Artifacts.zip',compress_type=zipfile.ZIP_STORED)
with zipfile.ZipFile(full) as z:
 assert z.testzip() is None
 for n,b in files.items():assert z.read(n)==b,n
 assert sha(z.read('Supplementary_Research_Artifacts.zip'))=='ee029862791413b993387234efe9ecad5114d99685ef5fd9d4add4eb53d080c8'
readme='''# Clean Neural Networks submission package

The scientific manuscript remains the final reviewed R7. The complete clean archive contains only journal-facing files; it contains no internal reviews, audit logs, old manuscript versions, response drafts, or restoration instructions.

## File roles for the submission portal

- Manuscript.pdf: reviewed 40-page article, unchanged.
- LaTeX_Source.zip: clean, complete editable source; main.tex is the entry point. It builds to the same rendered R7 PDF.
- Cover_Letter.pdf: updated transfer letter naming Neural Networks and Mathematical and Computational Analysis.
- Highlights.txt: five editable bullets, each within 85 characters.
- Title_Page.docx: preserved author details, affiliation, ORCID and keywords.
- Declaration_of_Competing_Interest.docx: preserved declaration.
- Figures/: seven separate vector PDF figures, unchanged.
- Supplementary_Research_Artifacts.zip: the complete unchanged 706024849-byte research supplement. Its original frozen filename was Supplementary_Research_Artifacts_R4.zip; only the outer filename has been cleaned.

The source ZIP includes the manuscript figures for compilation; the separate figure files are the same bytes for portal figure upload. Upload one version of each document in the portal's relevant category.

## Downloads

Neural_Networks_R7_Clean_Upload_Files.zip is the small upload set. It omits only the large numerical supplement. Use the supplement from the complete package or your existing verified R4 supplement, with SHA-256 ee029862791413b993387234efe9ecad5114d99685ef5fd9d4add4eb53d080c8.

The complete clean package is supplied in two transport ZIPs because of its size. Download both, extract into one folder, then run:

    python3 restore_clean_submission.py

This restores Neural_Networks_R7_Clean_Submission_Package.zip. Extract that archive to obtain the clean upload files and complete supplement together. The restoration script verifies both part hashes and the full archive before completing. The transport ZIPs themselves are download containers, not journal uploads.

## Preserved records and repository

The full R7 review, numerical audit and final baseline remain preserved separately. No journal reviewer-response document existed in the supplied release, so none was invented; independent-review responses remain author records. The existing GitHub repository is updated under journal/Neural_Networks_Submission_R7/. The original R7 folder and all trained evidence remain unchanged.

The direct Neural Networks author-guide page returned 403 during this preparation. Official Elsevier submission guidance was inspected; current portal file categories and author attestations must be checked when completing the transfer. The complete numerical supplement should accompany submission. The publisher's transfer/submission workflow has not been performed here.

Official guide attempted: https://www.sciencedirect.com/journal/neural-networks/publish/guide-for-authors
Official general file guidance: https://www.elsevier.support/publishing/answer/how-do-i-prepare-my-files-for-submission-in-editorial-manager
'''
(A/'UPLOAD_INSTRUCTIONS.md').write_text(readme)
data=full.read_bytes();size=(len(data)+1)//2;parts=[data[:size],data[size:]];meta={'archive':full.name,'bytes':len(data),'sha256':sha(data),'parts':[{'file':full.name+f'.part{i+1:03}','bytes':len(b),'sha256':sha(b)} for i,b in enumerate(parts)]}
restore='''from pathlib import Path
import hashlib,json,sys
r=Path(__file__).resolve().parent;m=json.loads((r/'CLEAN_SUBMISSION_SPLIT_MANIFEST.json').read_text())
def sha(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  for b in iter(lambda:f.read(1048576),b''):h.update(b)
 return h.hexdigest()
out=r/m['archive']
if out.exists():
 if out.stat().st_size==m['bytes'] and sha(out)==m['sha256']:print('PASS: exact clean package already exists.');sys.exit(0)
 raise SystemExit('Refusing to overwrite a different file.')
for p in m['parts']:
 f=r/p['file'];assert f.stat().st_size==p['bytes'] and sha(f)==p['sha256'],p['file']
tmp=out.with_suffix('.assembling')
with tmp.open('wb') as target:
 for p in m['parts']:
  with (r/p['file']).open('rb') as source:
   for b in iter(lambda:source.read(1048576),b''):target.write(b)
assert tmp.stat().st_size==m['bytes'] and sha(tmp)==m['sha256']
tmp.rename(out);print('PASS: clean submission package restored and verified.')
'''
paths=[];test=R/'tmp/clean_transport_restore';test.mkdir(exist_ok=True)
for i,b in enumerate(parts):
 p=O/f'Neural_Networks_R7_Clean_Submission_Part_{i+1}_of_2.zip'
 with zipfile.ZipFile(p,'w',zipfile.ZIP_STORED) as z:
  z.writestr(meta['parts'][i]['file'],b);z.writestr('restore_clean_submission.py',restore);z.writestr('CLEAN_SUBMISSION_SPLIT_MANIFEST.json',json.dumps(meta,indent=2)+'\n');z.writestr('UPLOAD_INSTRUCTIONS.md',readme)
 with zipfile.ZipFile(p) as z:assert z.testzip() is None;z.extractall(test)
 paths.append(p)
subprocess.run(['python',str(test/'restore_clean_submission.py')],check=True);assert sha((test/full.name).read_bytes())==meta['sha256']
receipt={'status':'PASS','manuscript_version':'R7_UNCHANGED','clean_files':list(files)+['Supplementary_Research_Artifacts.zip'],'journal_facing_files':len(files)+1,'internal_records_in_clean_archive':False,'full_archive':{k:v for k,v in meta.items() if k!='parts'},'small_upload_zip':{'file':small.name,'bytes':small.stat().st_size,'sha256':sha(small.read_bytes())},'transport_restore':'PASS','source_clean_build':'PASS_ALL40PAGES_IDENTICAL','parts':[{'file':str(p),'bytes':p.stat().st_size,'sha256':sha(p.read_bytes())} for p in paths],'journal_submission_complete':False}
(A/'CLEAN_PACKAGE_VERIFICATION.json').write_text(json.dumps(receipt,indent=2)+'\n')
request={'uploads':[{'local_path':str(p),'purpose':'create_library_file','library_artifact_type':t} for p,t in [(small,'other'),(paths[0],'other'),(paths[1],'other'),(A/'UPLOAD_INSTRUCTIONS.md','report')]]}
(R/'tmp/clean_upload_request.json').write_text(json.dumps(request));print(json.dumps(receipt))
