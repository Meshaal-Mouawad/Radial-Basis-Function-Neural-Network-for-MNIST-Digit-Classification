"""Build the R3 revision documents and portable, verified delivery archives."""
import difflib
import hashlib
import json
import re
import shutil
import sys
import zipfile
from pathlib import Path
from xml.sax.saxutils import escape

import fitz
import numpy
import scipy
import threadpoolctl
from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak

ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'output'
PKG=OUT/'RBF_Neural_Networks_R3'
JF=PKG/'journal_files'
REC=PKG/'revision_record'
OLD=ROOT/'baseline_R2/RBF_Neural_Networks_R2'
SRC=ROOT/'working_R3/source'
BASE=ROOT/'baseline_source'
DATE='14 November 2026'
TITLE='Training-Derived Regions of Nearest-Prototype Agreement in Gaussian RBF Classifiers'
for p in [OUT,JF,REC,PKG/'preserved_R2']:
    p.mkdir(parents=True,exist_ok=True)

def sha(path):
    h=hashlib.sha256()
    with Path(path).open('rb') as f:
        for b in iter(lambda:f.read(1<<20),b''):h.update(b)
    return h.hexdigest()

def js(path,obj):
    Path(path).write_text(json.dumps(obj,indent=2,ensure_ascii=False)+'\n')

def files(path):
    return sorted(p for p in Path(path).rglob('*') if p.is_file() and '__pycache__' not in p.parts)

def manifest(path):
    js(path/'SHA256_MANIFEST.json',{str(p.relative_to(path)):sha(p) for p in files(path) if p!=path/'SHA256_MANIFEST.json'})

def archive(path,dest,prefix=''):
    with zipfile.ZipFile(dest,'w',zipfile.ZIP_DEFLATED,compresslevel=6) as z:
        for p in files(path):z.write(p,prefix+str(p.relative_to(path)))

def para(text,style):return Paragraph(escape(text).replace('\n','<br/>'),style)

styles=getSampleStyleSheet()
styles.add(ParagraphStyle(name='TitleR3',fontName='Helvetica-Bold',fontSize=20,leading=24,textColor=colors.HexColor('#193449'),spaceAfter=14))
styles.add(ParagraphStyle(name='HeadR3',fontName='Helvetica-Bold',fontSize=12,leading=16,spaceBefore=13,spaceAfter=7,textColor=colors.HexColor('#193449')))
styles.add(ParagraphStyle(name='BodyR3',fontName='Helvetica',fontSize=10.5,leading=14.3,spaceAfter=8))
styles.add(ParagraphStyle(name='SmallR3',fontName='Helvetica',fontSize=9,leading=11.5,spaceAfter=6))
styles.add(ParagraphStyle(name='CellR3',fontName='Helvetica',fontSize=9,leading=11.5))

def footer(c,doc):
    c.setStrokeColor(colors.HexColor('#c7d2da'));c.line(48,42,564,42)
    c.setFont('Helvetica',8);c.setFillColor(colors.HexColor('#52616d'))
    c.drawString(48,29,'RBF / Neural Networks / R3 / 14 November 2026')
    c.drawRightString(564,29,str(doc.page))

def render(blocks,path):
    story=[]
    for kind,x in blocks:
        if kind=='title':story.append(para(x,styles['TitleR3']))
        elif kind=='h':story.append(para(x,styles['HeadR3']))
        elif kind=='p':story.append(para(x,styles['BodyR3']))
        elif kind=='small':story.append(para(x,styles['SmallR3']))
        elif kind=='page':story.append(PageBreak())
        elif kind=='table':
            data,widths=x
            t=Table([[para(c,styles['CellR3']) for c in row] for row in data],colWidths=widths,repeatRows=1,hAlign='LEFT')
            t.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,0),colors.HexColor('#e8eff4')),('VALIGN',(0,0),(-1,-1),'TOP'),('LINEBELOW',(0,0),(-1,0),.7,colors.HexColor('#667d8e')),('LINEBELOW',(0,-1),(-1,-1),.6,colors.HexColor('#b4c2cb')),('LEFTPADDING',(0,0),(-1,-1),7),('RIGHTPADDING',(0,0),(-1,-1),7),('TOPPADDING',(0,0),(-1,-1),7),('BOTTOMPADDING',(0,0),(-1,-1),7)]))
            story.extend([t,Spacer(1,9)])
    SimpleDocTemplate(str(path),pagesize=(612,792),rightMargin=48,leftMargin=48,topMargin=48,bottomMargin=58,title=path.stem.replace('_',' '),author='Meshaal Mouawad').build(story,onFirstPage=footer,onLaterPages=footer)

def markdown(blocks):
    out=[]
    for kind,x in blocks:
        if kind=='title':out.append('# '+x)
        elif kind=='h':out.append('## '+x)
        elif kind in ['p','small']:out.append(x)
        elif kind=='table':
            rows=x[0];out.append('\n'.join(['| '+' | '.join(rows[0])+' |','| '+' | '.join(['---']*len(rows[0]))+' |']+['| '+' | '.join(row)+' |' for row in rows[1:]]))
    return '\n\n'.join(out)+'\n'

# Protect the original scientific objects and compare the final rendered structure.
base=(BASE/'main.tex').read_text();new=(SRC/'main.tex').read_text()
protected=['results.tex','frontier_results.tex','ridge_theory.tex','exact_ridge_examples.tex','references.bib']
protected += [p.name for p in sorted(BASE.glob('*.pdf')) if p.name.startswith(('Fig','fig'))]
byte_checks={n:sha(BASE/n)==sha(SRC/n) for n in protected}
env_checks={}
for env in ['equation','theorem','lemma','proposition','proof']:
    pattern=r'\\begin\{'+env+r'\}.*?\\end\{'+env+r'\}'
    a=re.findall(pattern,base,re.S);b=re.findall(pattern,new,re.S)
    env_checks[env]={'count':len(a),'unchanged':a==b}
declaration='During preparation of this work, the author used Elsevier LeapSpace, other tools to support literature discovery, manuscript organization, language refinement, and consistency checking. The authors take responsibility for the content of the article.'
assert all(byte_checks.values()) and all(v['unchanged'] for v in env_checks.values())
assert base.count(declaration)==new.count(declaration)==1
doc=fitz.open(SRC/'main.pdf');text='\n'.join(p.get_text() for p in doc)
assert len(doc)==35 and 'Appendix Appendix' not in text and '(??)' not in text
log=(SRC/'main.log').read_text()
bad=[l for l in log.splitlines() if any(s in l for s in ['Overfull','Underfull','undefined','multiply defined'])]
assert not bad,bad
production={'status':'PASS','pages':len(doc),'figures':6,'tables':8,'bibliography_entries':len(re.findall(r'\\bibitem', (SRC/'main.bbl').read_text())), 'protected_files':byte_checks,'protected_math_environments':env_checks,'approved_AI_declaration_exact':True,'appendix_duplicate_count':text.count('Appendix Appendix'),'layout_or_reference_warnings':bad,'pdf_sha256':sha(SRC/'main.pdf'),'visual_inspection':'All pages inspected in contact sheets; new table page 29 inspected at full scale; final pages 34-35 inspected after bibliography spacing adjustment. No clipping, overlapping objects or unreadable tables found. Pages 1-33 retain the inspected layout.'}
js(REC/'PROTECTION_AND_PDF_AUDIT.json',production)
diff=''.join(difflib.unified_diff(base.splitlines(True),new.splitlines(True),fromfile='R2/main.tex',tofile='R3/main.tex'))
diff+=''.join(difflib.unified_diff((BASE/'new_results.tex').read_text().splitlines(True),(SRC/'new_results.tex').read_text().splitlines(True),fromfile='R2/new_results.tex',tofile='R3/new_results.tex'))
(REC/'R2_to_R3.diff').write_text(diff)

blocks=[
 ('title','R3 integrated revision report'),
 ('small',DATE+' | Neural Networks transfer preparation | Meshaal Mouawad'),
 ('p',TITLE),
 ('h','Completed outcome'),
 ('p','R3 implements the three pending scientific diagnostics directly in the R2 LaTeX manuscript. The compiled manuscript has 35 pages, six preserved figures, eight tables and 17 references. Numerical reconstruction, source preservation, cross-reference checks and page inspection passed.'),
 ('p','The authoritative starting point is the full R2 archive dated 9 November 2026. The recovered shared conversation contained proposed R3 work and an execution failure; it did not contain a completed integrated R3 source. This delivery completes that integration using the preserved R2 evidence.'),
 ('h','Change map'),
 ('table',([
  ['Finding','Implemented change','Manuscript location'],
  ['M1: reversal relevance','Reconstructed validation predictions for all 96 archived readouts per group; compared sufficient reversal bounds against same-width competitive penalties.','Section 5.6; Section 6.7; Table 6'],
  ['M2: exclusion overlap','Computed exact query-level unions and differences for original/dense limiting witnesses and original/all archived finite readouts.','Section 5.6; Section 6.8; Table 7'],
  ['M3: subset accuracy','Added equal-cardinality random, score, distance and agreement-gated baselines, plus selected class composition.','Section 5.6; Section 6.9; Table 8'],
  ['Editorial integration','Updated abstract, introduction, Discussion, Conclusion, Limitations and data availability; fixed duplicate appendix labels.','main.tex; new_results.tex; new r3_*.tex inputs']
 ],[100,276,140])),
 ('h','Research basis'),
 ('p','All three diagnostics retain the ten original K=100 dataset-seed groups. R3 scores archived models and reconstructs existing fitted weights. It adds no model fits and changes no original dataset, prototype identity, theorem, proof, approved figure or frozen result.'),
 ('page',''),
 ('title','Thresholds and exclusion overlap'),
 ('h','M1: sufficient bounds versus competitive readouts'),
 ('p','Competitive pairs achieve at least 95% of the best validation accuracy among the original 96 width-penalty pairs in their dataset-seed group. Each group uses its previously unused 5,000-image validation partition. The diagnostic reconstructs 4,800,000 validation prediction labels.'),
 ('p','At original widths with a competitive same-width reference, none of 150,814 strict-reversal query cases has a finite sufficient bound below the largest qualifying penalty. All 175,027 finite-bound checks at 1.001 times the bound give a strict competing fitted score. These counts use different eligibility sets; the abstract states the competitive-reference condition explicitly.'),
 ('table',([
 ['At width sC','MNIST','Fashion-MNIST'],
 ['Mean within-seed median bound / Gram norm','1.056','1.150'],
 ['Competitive maximum / Gram norm, range over seeds','0.0000318–0.0000344','0.00000291–0.0000298'],
 ['Bounds below competitive maximum / eligible cases','0 / 16,758','0 / 33,135']
 ],[232,142,142])),
 ('h','M2: contribution beyond finite checks'),
 ('p','L0 is the cumulative limiting-witness union over the original endpoints; L+ adds the 67-width frontier grid. F0 contains the original finite probes; F1 also includes eligible archived frontier and local-tail readouts. Every set comparison uses exactly matched query identifiers and requested parameter regions.'),
 ('table',([
 ['Unique exclusion at t = sC, floor 0','MNIST (%)','Fashion-MNIST (%)'],
 ['Original limit beyond original finite: L0 \\ F0','8.026','21.458'],
 ['Original limit beyond all archived finite: L0 \\ F1','0.000','0.134'],
 ['Dense limit beyond all archived finite: L+ \\ F1','0.000','0.148']
 ],[300,108,108])),
 ('p','All 210 original R2 region counts are recovered exactly. The 0.134% Fashion-MNIST value represents 67 seed-query cases. At 2sC the dense limit retains 12.950% unique Fashion-MNIST exclusions; the archived high-penalty local-tail fits are concentrated near sC/2 and sC. The manuscript identifies this finite-sampling relationship.'),
 ('page',''),
 ('title','Matched-coverage selection'),
 ('p','Each comparator selects exactly the certificate count within each seed. Ranking uses model scores or prototype distances without evaluation labels, with deterministic ties. The random result is the exact expected accuracy of a uniform subset of that cardinality. Primary score margins use actual Gaussian fitted scores; normalized-score sensitivity is retained in the supplement.'),
 ('table',([
 ['Endpoint accuracy, mean %','MNIST sC/2','MNIST sC','Fashion sC/2','Fashion sC'],
 ['Certificate','69.09','68.93','75.27','64.65'],
 ['Random expectation','15.60','11.77','45.06','29.86'],
 ['Score margin','67.87','66.05','65.19','57.21'],
 ['Distance margin','41.11','28.05','60.11','31.01'],
 ['Agreement-gated score','69.17','68.93','76.13','64.47'],
 ['Agreement-gated distance','85.55','68.93','79.34','82.94']
 ],[184,83,83,83,83])),
 ('p','The certificate exceeds random and ordinary score-margin selection in all four reported means. Agreement-gated distance selection is more accurate in three conditions and selects the identical set in the fourth. The manuscript reports this strongest comparator in both the abstract and Results.'),
 ('p','At the MNIST endpoint t=sC and penalty 10 times the Gram norm, every prediction is class 1. Its full-query accuracy is exactly 474/4,027 = 11.77055%. The certificate selects the complete endpoint-agreement pool. At sC/2, class 1 accounts for 99.45% of certified predictions. At Fashion-MNIST t=sC, class 7 accounts for 80.94%. These class distributions explain the selected-set composition.'),
 ('h','Independent numerical verification'),
 ('table',([
 ['Independent reconstruction','Verified count / outcome'],
 ['Validation prediction labels','4,800,000; exact match'],
 ['Threshold records / finite reversals','490,945 / 175,027; zero reversal failures'],
 ['Endpoint labels / selector masks','140,270 / 120; exact match'],
 ['Selector rows / class-count rows','140 / 1,400; exact match'],
 ['Original region unions','210; exact recovery'],
 ['Largest threshold relative discrepancy','1.237 × 10^-10; within declared tolerance']
 ],[280,236])),
 ('page',''),
 ('title','Preservation and delivery record'),
 ('h','Protected content and production checks'),
 ('p','All six figure PDFs, results.tex, frontier_results.tex, ridge_theory.tex, exact_ridge_examples.tex and references.bib match R2 byte for byte. The original 17 numbered equation environments, one theorem, two lemmas, two propositions and five proofs in main.tex are exact. The additional R2 theory is preserved through exact file identity. The author-approved AI declaration is exact and appears once.'),
 ('p','The LaTeX build completes without overfull/underfull boxes, unresolved references or duplicate labels. All 35 final pages were inspected, including the three new tables. Bibliography spacing was reduced to 2 pt between items to remove an almost empty final page; no reference was removed.'),
 ('h','Archive contents and reproduction'),
 ('p','journal_files contains the compiled manuscript, standalone LaTeX ZIP, self-contained numerical supplement, updated draft cover letter and highlights, and the preserved title-page and competing-interest files. revision_record contains this report, source diff, preservation audit, independent review, build logs and integration scripts. preserved_R2 contains the original R2 manuscript and source ZIP.'),
 ('p','The supplement includes the complete R2 research evidence under evidence/ and the new protocols, scripts, CSV summaries, query-level arrays, hashes and independent checks under r3_analysis/. Its README gives verification and full-regeneration commands. Each delivery archive has a SHA-256 manifest; verify_package.py checks the outer files and nested source/supplement manifests.'),
 ('p','Current runtime: Python 3.12.14, NumPy 2.3.5, SciPy 1.17.0 and threadpoolctl 3.6.0. The original frozen environment remains documented with its evidence. The container lacked a prebuilt pdfLaTeX format and font map; a local format and maps were generated from its existing TeX installation. Standard LaTeX commands are documented in the source ZIP.'),
 ('h','Status'),
 ('p','R3 is the next internal manuscript version, prepared for the selected Neural Networks transfer. It is not a journal-assigned revision number. The transfer/submission process remains incomplete.'),
 ('h','Limitations and outstanding decision'),
 ('p','The three requested analyses and production corrections are complete. A demonstrated predictive or model-selection benefit at competitive penalties remains unresolved; these numerical findings do not settle the editor’s significance concern. Their interpretation is confined to the recorded models and sampling design. The official Neural Networks author guide returned HTTP 403 during verification, so current anonymity rules and portal-specific upload requirements have not been certified. No external submission was performed.'),
 ('small','Official venue pages consulted: https://shop.elsevier.com/journals/neural-networks/0893-6080 ; https://www.sciencedirect.com/journal/neural-networks/publish/guide-for-authors ; https://www.elsevier.support/publishing/answer/how-do-i-prepare-my-files-for-submission-in-editorial-manager')
]
reportname='RBF_Neural_Networks_Revision_Report_R3'
(REC/(reportname+'.md')).write_text(markdown(blocks))
render(blocks,REC/(reportname+'.pdf'))

cover=[('title','Transfer manuscript: Neural Networks'),('small',DATE),('p','Dear Editor,'),('p','Please consider '+TITLE+' as a research article. The manuscript was previously submitted to Neurocomputing under NEUCOM-D-26-25836; I selected Neural Networks for the proposed transfer. This R3 version adds direct numerical analyses relevant to the prior concern about significance.'),('p','The work develops training-derived conditions for nearest-prototype agreement in Gaussian ridge radial basis function classifier families. Its mathematical results certify continuous bandwidth-penalty regions, identify strict large-penalty exclusions with finite disagreement bounds, and certify local bandwidth bands and penalty tails.'),('p','The revision evaluates sufficient reversal bounds against validation-based competitive models, measures exact exclusion overlap with all archived finite readouts, and compares certified subsets with informed selectors at identical coverage. These analyses retain all ten original 100-prototype dataset-seed groups. They quantify the reach of the analytical guarantees and connect selected-set accuracy to class composition.'),('p','The manuscript preserves the original proofs, evidence and six figures. Three additional tables report the new diagnostics. The accompanying supplement includes protocols, per-query records, reproducible scripts, hashes and independent numerical reconstruction. The contribution is a verified analysis of continuous decision persistence in a conventional RBF classifier family.'),('p','Thank you for considering the revised work.'),('p','Meshaal Mouawad\nDepartment of Electrical and Computer Engineering\nMississippi State University\nMississippi State, MS 39762, USA\nmm4922@msstate.edu')]
covername='Cover_Letter_Neural_Networks_R3'
(JF/(covername+'.md')).write_text(markdown(cover));render(cover,JF/(covername+'.pdf'))
highlights=[
 'Training-derived tests certify agreement across RBF parameter regions.',
 'Strict limiting votes provide finite disagreement bounds.',
 'Validation comparisons locate sufficient reversals on the penalty path.',
 'Exact witness unions quantify exclusions beyond archived finite readouts.',
 'Matched-coverage selectors reveal the role of selected class composition.'
]
assert all(len(x)<=85 for x in highlights)
(JF/'Highlights_Neural_Networks_R3.txt').write_text('\n'.join('- '+x for x in highlights)+'\n')
for n in ['Title_Page.docx','Title_Page.pdf','Declaration_of_Competing_Interest.docx','Declaration_of_Competing_Interest.pdf']:
    shutil.copy2(OLD/'journal_files'/n,JF/n)
shutil.copy2(SRC/'main.pdf',JF/'RBF_Neural_Networks_Manuscript_R3.pdf')
for n in ['RBF_Neural_Networks_Manuscript_R2.pdf','LaTeX_Source_Neural_Networks_R2.zip']:
    shutil.copy2(OLD/'journal_files'/n,PKG/'preserved_R2'/n)
for p in (ROOT/'r3_analysis/review').glob('*.md'):shutil.copy2(p,REC/p.name)
for p in (ROOT/'logs').glob('*.log'):shutil.copy2(p,REC/p.name)
for p in (ROOT/'r3_analysis/integration').glob('*.py'):
    (REC/'integration_scripts').mkdir(exist_ok=True);shutil.copy2(p,REC/'integration_scripts'/p.name)
js(REC/'INPUT_PROVENANCE.json',{'R2_archive':'RBF_Neural_Networks_Full_Revision_R2_2026-11-09.zip','R2_sha256':sha(ROOT/'inputs/RBF_Neural_Networks_Full_Revision_R2_2026-11-09.zip'),'shared_handoff':'https://chatgpt.com/share/6af8a079-6d60-83eb-a80a-b027b12ae2da','revision_date':DATE,'runtime':{'python':sys.version,'numpy':numpy.__version__,'scipy':scipy.__version__,'threadpoolctl':threadpoolctl.__version__}})

source_stage=ROOT/'tmp/delivery_source';source_stage.mkdir(exist_ok=True)
for p in SRC.iterdir():
    if p.suffix in ['.tex','.bib','.bbl','.cls','.bst','.dtx','.ins','.svg','.png'] or (p.suffix=='.pdf' and p.name!='main.pdf'):
        shutil.copy2(p,source_stage/p.name)
(source_stage/'README.md').write_text('''# R3 manuscript source

Training-Derived Regions of Nearest-Prototype Agreement in Gaussian RBF Classifiers
Target: Neural Networks. Internal version R3, 14 November 2026.
The transfer remains incomplete; R3 is not a journal-issued revision number.

Compile from this directory with a standard TeX installation:

    latexmk -pdf -interaction=nonstopmode -halt-on-error main.tex

Alternatively: pdflatex main.tex, bibtex main, pdflatex main.tex, pdflatex main.tex.
The verified PDF has 35 pages, six figures, eight tables and 17 references.
All original figures, equations, proofs, frozen results and the approved AI
declaration are preserved. r3_methods.tex and r3_results.tex integrate the new
diagnostics; the three r3_*_table.tex files are generated from verified CSVs.
The companion supplement contains the complete numerical evidence.
SHA256_MANIFEST.json covers every other file in this source archive.
''')
manifest(source_stage);archive(source_stage,JF/'LaTeX_Source_Neural_Networks_R3.zip')

supp=ROOT/'tmp/delivery_supplement';supp.mkdir(exist_ok=True)
# Copy only the original named R2 entries, retaining their exact bytes.
with zipfile.ZipFile(OLD/'journal_files/Supplementary_Research_Artifacts_R2.zip') as z:
    for name in z.namelist():
        if name.endswith('/'):continue
        p=supp/'evidence'/name;p.parent.mkdir(parents=True,exist_ok=True)
        original=z.read(name);assert original==(ROOT/'evidence'/name).read_bytes(),name
        p.write_bytes(original)
for name in ['m1_m2','m3','independent','verification']:
    for p in files(ROOT/'r3_analysis'/name):
        target=supp/'r3_analysis'/name/p.relative_to(ROOT/'r3_analysis'/name)
        target.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,target)
(supp/'README_R3.md').write_text('''# R3 numerical supplement

Unzip into an empty directory and retain evidence/ and r3_analysis/ together.
evidence/ is the complete original R2 supplement, unchanged. r3_analysis/
contains the new recorded protocols, scripts, outputs and verification.
R3 performs no new fits. Its validation scores and comparisons use archived
readouts. Numerical requirements: Python 3.12, numpy==2.3.5, scipy==1.17.0,
threadpoolctl==3.6.0. Additional original requirements remain under evidence/.

From this extracted root, verify hashes first:

    python verify_package.py

Then independently reconstruct the new results:

    PYTHONDONTWRITEBYTECODE=1 python r3_analysis/independent/verify_r3.py
    PYTHONDONTWRITEBYTECODE=1 python r3_analysis/m1_m2/verify_outputs.py
    PYTHONDONTWRITEBYTECODE=1 python r3_analysis/m3/verify_m3.py
    PYTHONDONTWRITEBYTECODE=1 python r3_analysis/verification/reconstruct_r2_arrays.py

The independent and M3/R2 verification scripts refresh their adjacent JSON
reports; elapsed time may differ. Run those checks in a disposable extracted
copy after manifest verification, so the delivered records remain intact.

To regenerate all R3 analysis outputs in a disposable copy:

    PYTHONDONTWRITEBYTECODE=1 python r3_analysis/m1_m2/run_analysis.py
    PYTHONDONTWRITECODE=1 python r3_analysis/m3/run_m3.py

The original R2 verification commands are documented in evidence/README.md.
The highest-cost original pipelines are unnecessary for checking the new
results. Every new numerical table retains seed-level and per-query evidence.
'''.replace('PYTHONDONTWRITECODE','PYTHONDONTWRITEBYTECODE'))
(supp/'requirements_R3.txt').write_text('numpy==2.3.5\nscipy==1.17.0\nthreadpoolctl==3.6.0\n')
verify_code='''#!/usr/bin/env python3
"""Check the complete archive and manifests inside any nested ZIP files."""
import hashlib,json,zipfile
from pathlib import Path
root=Path(__file__).resolve().parent
def digest(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  for b in iter(lambda:f.read(1048576),b''):h.update(b)
 return h.hexdigest()
manifest=json.loads((root/'SHA256_MANIFEST.json').read_text())
for name,value in manifest.items():
 assert digest(root/name)==value,name
nested=0
for path in root.rglob('*.zip'):
 with zipfile.ZipFile(path) as z:
  assert z.testzip() is None,str(path)
  if 'SHA256_MANIFEST.json' in z.namelist():
   for name,value in json.loads(z.read('SHA256_MANIFEST.json')).items():
    assert hashlib.sha256(z.read(name)).hexdigest()==value,(str(path),name)
    nested+=1
print(json.dumps({'status':'PASS','files_verified':len(manifest),'nested_manifest_entries_verified':nested}))
'''
(supp/'verify_package.py').write_text(verify_code)
manifest(supp);archive(supp,JF/'Supplementary_Research_Artifacts_R3.zip')
(PKG/'verify_package.py').write_text(verify_code)
(PKG/'README.md').write_text('''# Neural Networks — integrated R3 revision

14 November 2026. The selected transfer remains pending.

Start with journal_files/RBF_Neural_Networks_Manuscript_R3.pdf and the revision
report in revision_record/. This is an integrated, compiled 35-page manuscript
with six preserved figures, eight tables and the complete research supplement.

journal_files/: editable source ZIP, compiled PDF, numerical supplement,
updated draft cover letter/highlights, preserved title page/interest declaration.
revision_record/: report, reviews, preservation/PDF audit, source diff and logs.
preserved_R2/: authoritative R2 manuscript and source ZIP for comparison.

From this folder run: python verify_package.py
Then extract Supplementary_Research_Artifacts_R3.zip and follow README_R3.md.
The source ZIP is independently compilable; see its README.md.

To replay editorial integration in a scratch folder, extract the R2 source to
baseline_source/ and the R3 source to working_R3/source/. Copy integration_scripts/
into r3_analysis/integration/. Extract the numerical supplement alongside those
directories. Run integrate_manuscript.py, then build_tables.py --output
working_R3/source. Recompile. The delivery-building script records production
steps for this workspace; the standalone source and numerical verifiers are
the portable reproduction entry points.

The requested R3 analyses and source changes are complete. Scientific impact
at competitive penalties remains an open research decision, as explained in
the report and manuscript Limitations. Portal-specific requirements remain
unverified. No journal submission has been made from this workspace.
''')
manifest(PKG)
for p in [JF/'RBF_Neural_Networks_Manuscript_R3.pdf',JF/'LaTeX_Source_Neural_Networks_R3.zip',REC/(reportname+'.pdf')]:
    shutil.copy2(p,OUT/p.name)
archive(PKG,OUT/'RBF_Neural_Networks_Full_Revision_R3_2026-11-14.zip',PKG.name+'/')
print(json.dumps({'status':'BUILT','production':production,'output_files':[{'name':p.name,'bytes':p.stat().st_size} for p in OUT.iterdir() if p.is_file()]},indent=2))
