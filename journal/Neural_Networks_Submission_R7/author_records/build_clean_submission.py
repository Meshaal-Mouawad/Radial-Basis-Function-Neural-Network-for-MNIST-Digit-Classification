from pathlib import Path
import zipfile,hashlib,json,shutil,re
from xml.sax.saxutils import escape
from reportlab.platypus import SimpleDocTemplate,Paragraph,Spacer
from reportlab.lib.styles import getSampleStyleSheet,ParagraphStyle
R=Path(__file__).resolve().parents[1];P=R/'submission_clean';U=P/'journal_upload';U.mkdir(parents=True,exist_ok=True);A=P/'author_records';A.mkdir(exist_ok=True)
S=R/'output/RBF_Neural_Networks_R7';J=R/'restored/full_R5/RBF_Neural_Networks_R5/journal_files';sha=lambda b:hashlib.sha256(b).hexdigest()
shutil.copy2(S/'RBF_Neural_Networks_Manuscript_R7.pdf',U/'Manuscript.pdf')
for n in ['Title_Page.docx','Declaration_of_Competing_Interest.docx']:shutil.copy2(J/n,U/n)
hl=(J/'Highlights_Neural_Networks_R5.txt').read_text();(U/'Highlights.txt').write_text(hl)
bullets=[x[2:] for x in hl.splitlines() if x.startswith('- ')];assert len(bullets)==5 and all(len(x)<=85 for x in bullets)
sources={}
with zipfile.ZipFile(S/'LaTeX_Source_Neural_Networks_R7.zip') as z:
 for n in z.namelist():
  if n.endswith(('.tex','.bib','.bbl','.cls','.bst','.pdf')):sources[n]=z.read(n)
assert 'main.tex' in sources and sha(sources['main.tex'])=='71d01178d02cfddf8f980b58239b6242329b5b73bbe0a0347f2358bd33900ad6'
with zipfile.ZipFile(U/'LaTeX_Source.zip','w',zipfile.ZIP_DEFLATED) as z:
 for n,b in sources.items():
  i=zipfile.ZipInfo(n,date_time=(2026,11,17,0,0,0));i.compress_type=zipfile.ZIP_DEFLATED;z.writestr(i,b)
fig=U/'Figures';fig.mkdir(exist_ok=True)
for n,b in sources.items():
 if n.startswith('Figure_') and n.endswith('.pdf'):(fig/n).write_bytes(b)
assert len(list(fig.iterdir()))==7
cover='''17 November 2026

Dear Editor,

Please consider “Training-Derived Regions of Nearest-Prototype Agreement in Gaussian RBF Classifiers” for publication as a research article in Neural Networks, in the Mathematical and Computational Analysis section. The manuscript was previously submitted to Neurocomputing under NEUCOM-D-26-25836, and I selected Neural Networks for the proposed transfer.

A nearest prototype supplies a simple label summary for a radial basis function classifier, yet learned output weights can produce a different class. This manuscript determines when that summary remains valid as Gaussian bandwidth and ridge regularization change. Training-derived inequalities certify agreement across continuous parameter regions, strict witnesses exclude whole-region agreement, and a signed local-band construction certifies additional regions at sufficiently large penalties.

The evaluation uses MNIST and Fashion-MNIST, five seeds, three prototype budgets and 2,880 archived readouts. All 328 readouts meeting the primary validation-competitive rule have zero full-width certificate coverage. Finite penalty paths exhibit returns to agreement after disagreement, and matched-coverage, class-conditioned comparisons explain the composition of certified subsets. These findings establish the empirical reach of the guarantees and connect parameter-dependent label persistence to predictive behavior.

The accompanying complete numerical supplement contains the preserved training evidence, fitted weights, indexed splits, protocols, analysis scripts, per-query records and independent reconstruction checks. The LaTeX source and seven figures are supplied separately.

Thank you for considering the manuscript.

Meshaal Mouawad
Department of Electrical and Computer Engineering
Mississippi State University
mm4922@msstate.edu
'''
(A/'Cover_Letter.md').write_text(cover)
styles=getSampleStyleSheet();styles.add(ParagraphStyle(name='CleanLetter',fontName='Helvetica',fontSize=10.5,leading=14,spaceAfter=11));flow=[]
for p in cover.split('\n\n'):
 if p.strip():flow.append(Paragraph(escape(p.strip()).replace('\n','<br/>'),styles['CleanLetter']))
SimpleDocTemplate(str(U/'Cover_Letter.pdf'),pagesize=(595,842),leftMargin=52,rightMargin=52,topMargin=48,bottomMargin=48,author='Meshaal Mouawad',title='Cover letter to Neural Networks').build(flow)
clean=R/'tmp/clean_submission_source';clean.mkdir(parents=True,exist_ok=True)
with zipfile.ZipFile(U/'LaTeX_Source.zip') as z:z.extractall(clean)
supp=J/'Supplementary_Research_Artifacts_R4.zip';assert sha(supp.read_bytes())=='ee029862791413b993387234efe9ecad5114d99685ef5fd9d4add4eb53d080c8'
manifest={str(p.relative_to(U)):sha(p.read_bytes()) for p in sorted(U.rglob('*')) if p.is_file()};manifest['Supplementary_Research_Artifacts.zip']=sha(supp.read_bytes())
(A/'JOURNAL_UPLOAD_SHA256.json').write_text(json.dumps(manifest,indent=2)+'\n')
record={'status':'STAGED_FOR_FINAL_CHECK','manuscript_baseline':'R7_UNCHANGED','reviewed_commit':'93b4b15a3c2c643a67f45b2146b67a0acd4dfca4','manuscript_sha256':sha((U/'Manuscript.pdf').read_bytes()),'science_source_main_sha256':sha(sources['main.tex']),'source_members':len(sources),'figures':7,'highlight_characters':[len(x) for x in bullets],'new_training_runs':0,'reviewer_response':'No journal reviewer-response document exists; independent reviews retained outside journal upload','removed_from_source_package':['unused PNG/SVG previews','class development dtx/ins files','release README and checksum metadata'],'live_journal_guide':'403 on official direct access; generic publisher submission instructions inspected, portal-specific requirements remain to be checked during upload','journal_submission_complete':False}
(A/'PREPARATION_RECORD.json').write_text(json.dumps(record,indent=2)+'\n')
print(json.dumps(record))
