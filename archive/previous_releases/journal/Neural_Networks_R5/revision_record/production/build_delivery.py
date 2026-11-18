"""Build R5 editorial delivery from frozen R4 science; no model execution."""
from pathlib import Path
from datetime import datetime
from zoneinfo import ZoneInfo
import difflib, hashlib, json, re, shutil, zipfile
import fitz
from xml.sax.saxutils import escape
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak

ROOT = Path(__file__).resolve().parents[1]
S = ROOT/'working_R5/source'
BASE = ROOT/'working_R4/source'
OUT = ROOT/'output'
PKG = OUT/'RBF_Neural_Networks_R5'
JF, REC = PKG/'journal_files', PKG/'revision_record'
STAGE = ROOT/'tmp/r5_delivery/source'
DATE = datetime.now(ZoneInfo('Asia/Riyadh')).date().isoformat()
for p in [JF, REC, STAGE]: p.mkdir(parents=True, exist_ok=True)

def sha(p):
    h = hashlib.sha256()
    with Path(p).open('rb') as f:
        for b in iter(lambda: f.read(1048576), b''): h.update(b)
    return h.hexdigest()

def js(p, v): Path(p).write_text(json.dumps(v, indent=2)+'\n')

def files(p): return sorted(x for x in Path(p).rglob('*') if x.is_file() and '__pycache__' not in x.parts)

def manifest(p): js(p/'SHA256_MANIFEST.json', {str(x.relative_to(p)): sha(x) for x in files(p) if x.name != 'SHA256_MANIFEST.json'})

def archive(p, out):
    with zipfile.ZipFile(out, 'w') as z:
        for x in files(p):
            z.write(x, str(x.relative_to(p)), compress_type=zipfile.ZIP_STORED if x.suffix=='.zip' else zipfile.ZIP_DEFLATED, compresslevel=6)

# Protect source mathematics, result inputs, original bibliographic records and data.
a, b = (BASE/'main.tex').read_text(), (S/'main.tex').read_text()
baseline = json.loads((ROOT/'r5_editorial/R4_BASELINE_HASHES.json').read_text())
assert all(sha(ROOT/p)==h for p,h in baseline.items()), 'R4 baseline changed'
protected = {p.name: sha(p)==sha(S/p.name) for p in BASE.iterdir()
             if p.is_file() and (S/p.name).exists() and p.name not in ['main.tex','references.bib','main.bbl','main.pdf','main.log','main.aux','main.blg','main.fls','main.fdb_latexmk','main.out','main.spl']}
assert all(protected.values()), protected
math = {}
for env in ['equation','theorem','lemma','proposition','proof']:
    pat = r'\\begin\{'+env+r'\}.*?\\end\{'+env+r'\}'
    x,y = re.findall(pat,a,re.S), re.findall(pat,b,re.S)
    math[env]={'count':len(x),'exact':x==y}
assert all(v['exact'] for v in math.values())
for start, end in [(r'\section{Model and training-derived quantities}', r'\section{Conclusion}'),
                   (r'\section{Limitations}',r'\bibliographystyle')]:
    assert a[a.index(start):a.index(end)] == b[b.index(start):b.index(end)], start
original_bib=(BASE/'references.bib').read_text()
assert (S/'references.bib').read_text().startswith(original_bib), 'Original references altered'
declaration='During preparation of this work, the author used Elsevier LeapSpace, other tools to support literature discovery, manuscript organization, language refinement, and consistency checking. The authors take responsibility for the content of the article.'
assert a.count(declaration)==b.count(declaration)==1
pdf=fitz.open(S/'main.pdf'); pages=len(pdf)
assert pages==40, pages
abstract=b.split(r'\begin{abstract}')[1].split(r'\end{abstract}')[0].strip()
word_count=len(abstract.split()); assert word_count<250
assert len(re.findall(r'\\bibitem', (S/'main.bbl').read_text()))==18
warnings=[s for s in (S/'main.log').read_text().splitlines() if any(w in s for w in ['Warning','Overfull','Underfull','undefined','multiply defined'])]
assert not warnings, warnings
pdftext='\n'.join(p.get_text() for p in pdf)
assert 'Appendix Appendix' not in pdftext and '(??)' not in pdftext
assert 'We establish training-derived' not in abstract
supp=ROOT/'output/RBF_Neural_Networks_R4/journal_files/Supplementary_Research_Artifacts_R4.zip'
supp_hash=sha(supp)
assert supp_hash=='ee029862791413b993387234efe9ecad5114d99685ef5fd9d4add4eb53d080c8'
for n in ['composition','competitive','paths_efficiency','summary_tables']:
    assert json.loads((ROOT/f'r4_analysis/independent/{n}_verification.json').read_text())['status']=='PASS'
js(REC/'PRESERVATION_AUDIT.json', {
    'status':'PASS','date':DATE,'R4_source_checkpoint_unchanged':True,
    'protected_source_files':protected,'main_math_environments':math,
    'model_theory_methods_results_discussion_unchanged':True,
    'limitations_appendices_and_declarations_unchanged':True,
    'original_17_bib_entries_byte_preserved':True,'new_reference':'srihari1979',
    'approved_AI_declaration_exact_and_once':True,'pages':pages,'figures':7,'tables':12,
    'references':18,'abstract_whitespace_word_count':word_count,'build_warnings':warnings,
    'numerical_supplement_sha256':supp_hash,'numerical_supplement_bytes':supp.stat().st_size,
    'new_training_runs':0,'new_numerical_analyses':0,'main_tex_sha256':sha(S/'main.tex'),
    'manuscript_pdf_sha256':sha(S/'main.pdf')})

for name in ['main.tex','references.bib']:
    diff=''.join(difflib.unified_diff((BASE/name).read_text().splitlines(True),(S/name).read_text().splitlines(True),fromfile='R4/'+name,tofile='R5/'+name))
    (REC/(name.replace('.','_')+'_R4_to_R5.diff')).write_text(diff)
for p in files(ROOT/'r5_editorial/review'):
    q=REC/'editorial_reviews'/p.relative_to(ROOT/'r5_editorial/review');q.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,q)
shutil.copy2(ROOT/'logs/r5_build.log', REC/'r5_build.log')
shutil.copy2(ROOT/'r5_editorial/R4_BASELINE_HASHES.json', REC/'R4_BASELINE_HASHES.json')
shutil.copytree(ROOT/'r4_closure', REC/'R4_completed_plan', dirs_exist_ok=True)
shutil.copytree(ROOT/'r4_analysis/independent', REC/'R4_numerical_verification', dirs_exist_ok=True, ignore=shutil.ignore_patterns('__pycache__'))
(REC/'production').mkdir(exist_ok=True)
shutil.copy2(__file__,REC/'production/build_delivery.py')

styles=getSampleStyleSheet()
for name,size,leading in [('Title5',20,24),('HeadR5',12,16),('Body5',10,14),('Small5',8.8,12),('Cell5',9,12)]:
    styles.add(ParagraphStyle(name=name,fontName='Helvetica-Bold' if name in ['Title5','HeadR5'] else 'Helvetica',fontSize=size,leading=leading,textColor=colors.HexColor('#173348'),spaceAfter=8))
def paragraph(t,style):return Paragraph(escape(t).replace('\n','<br/>'),styles[style])
def footer(c,doc):
    c.setFont('Helvetica',8);c.setFillColor(colors.HexColor('#51616e'));c.drawString(48,30,'RBF / Neural Networks / R5 / '+DATE);c.drawRightString(564,30,str(doc.page))
def document(blocks,folder,stem):
    story=[];md=[]
    for kind,t in blocks:
        if kind=='page':story.append(PageBreak());continue
        if kind=='table':
            rows,widths=t
            tab=Table([[paragraph(str(c),'Cell5') for c in row] for row in rows],colWidths=widths,repeatRows=1)
            tab.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,0),colors.HexColor('#e8eef3')),('VALIGN',(0,0),(-1,-1),'TOP'),('LINEBELOW',(0,0),(-1,0),.6,colors.HexColor('#6e8393')),('TOPPADDING',(0,0),(-1,-1),6),('BOTTOMPADDING',(0,0),(-1,-1),6)]))
            story.extend([tab,Spacer(1,8)])
            md.append('\n'.join(['| '+' | '.join(rows[0])+' |','| '+' | '.join(['---']*len(rows[0]))+' |']+['| '+' | '.join(row)+' |' for row in rows[1:]]))
        else:
            style={'title':'Title5','head':'HeadR5','body':'Body5','small':'Small5'}[kind]
            story.append(paragraph(t,style));md.append(('# ' if kind=='title' else '## ' if kind=='head' else '')+t)
    (folder/(stem+'.md')).write_text('\n\n'.join(md)+'\n')
    SimpleDocTemplate(str(folder/(stem+'.pdf')),pagesize=(612,792),leftMargin=48,rightMargin=48,topMargin=46,bottomMargin=56,title=stem.replace('_',' '),author='Meshaal Mouawad').build(story,onFirstPage=footer,onLaterPages=footer)

report=[('title','R5 editorial revision report'),('small',DATE+' | Integrated LaTeX revision | Neural Networks'),
('head','Completed correction'),
('body',f'The abstract now begins with the relationship between prototype similarity and the fitted prediction. It introduces the unresolved parameter-region question before the method and evidence. The revised abstract has {word_count} words. The introduction, related work, comparison table and conclusion are integrated into the actual LaTeX source. The compiled manuscript has 40 pages, seven figures, twelve tables and eighteen references.'),
('table',([['Location','Problem corrected','Integrated change'],
['Abstract','The contribution appeared before the reader understood its purpose.','Context, decision mismatch, research question, method, principal evidence and contribution now form one connected progression. The numerical sentence specifies 100 prototypes and the zero penalty floor.'],
['Introduction','Technical machinery and a catalogue of analyses interrupted the motivation.','The two label calculations are explained first. Parameter variation motivates the research question; the three region outcomes then introduce the approach.'],
['Related work / Table 1','Repeated gap statements obscured the relationship among studies.','The review now connects nearest versus aggregate decisions, scale and regularization, and the object varied by a certificate. Srihari, White and Snabb (1979) adds the directly relevant finite-scale predecessor.'],
['Conclusion / layout','The ending repeated the construction inventory; the added reference created an orphan page.','The conclusion returns to the label-summary question and measured findings. Standard bibliography spacing keeps the final references together.']],[91,180,245])),
('body','All original findings remain in the manuscript, including zero full-width coverage among the 328 validation-competitive readouts, finite-path returns, exact witness overlaps, and class-conditioned subset results. No scientific interpretation was changed to make the contribution appear stronger.'),
('page',''),('title','Verification and review handoff'),
('head','Evidence preservation'),
('body','The original seventeen bibliography entries are unchanged; one verified historical reference is appended. Every included theory, method, result and result-table file is unchanged. All seven figure files are unchanged, including the six approved original figures. The main-source mathematical environments, experimental design, Discussion, Limitations, appendices and approved AI declaration are preserved. The complete R4 numerical supplement is included byte for byte.'),
('head','Independent checks'),
('body','Two separate configured GPT-6.1 Sol / High agents checked (1) primary-source attributions and their integration, and (2) first-time-reader comprehension and claim conditions. Both checks passed on the final source. The reader review identified the missing zero-floor condition in the abstract; it is resolved. A further local definition makes the validation comparison self-contained. The exact file hashes and review records accompany this report.'),
('body','The manuscript was compiled with the Elsevier class, rendered, and visually inspected across all pages. The build has no missing references, citation warnings or box warnings. Fresh extraction, compilation and rendered-page comparison are recorded separately in the production receipt.'),
('head','Cost and data reuse'),
('body','R5 is an editorial revision. It adds zero training runs and zero new numerical analyses. It retains the complete expensive training evidence and the independently verified R3/R4 analyses. The two focused Sol / High checks handle the editorial risk without repeating the computational pipeline. The original A-I plan closure, numerical audits and independent scientific review remain in revision_record/.'),
('head','Completion status'),
('body','The requested opening and argument revision is complete and ready for independent review. The full package contains the compiled manuscript, standalone LaTeX source, unchanged complete numerical supplement, source differences, verification records, title page, declarations, draft cover letter and highlights. The existing GitHub repository receives the R5 source and review artifacts; its preserved research history remains intact. Neural Networks transfer/submission is still pending.'),
('head','Verification boundary'),
('body','The current ScienceDirect author-guide page returned HTTP 403. The revision follows the supplied academic-writing guidance and preserves the existing Elsevier template. This editorial check does not certify a submission-portal checklist. The completed R4 independent scientific assessment remains the scientific review of the underlying evidence; R5 adds clarity and source-attribution reviews.')]
document(report,REC,'RBF_Neural_Networks_Revision_Report_R5')
cover=[('title','Transfer manuscript: Neural Networks'),('small',DATE+' | Draft cover letter'),('body','Dear Editor,'),
('body','Please consider Training-Derived Regions of Nearest-Prototype Agreement in Gaussian RBF Classifiers as a research article. The manuscript was previously submitted to Neurocomputing under NEUCOM-D-26-25836, and I selected Neural Networks for the proposed transfer.'),
('body','A nearest prototype offers a simple label summary for a radial basis function classifier. The learned output weights can produce a different class, creating a question about when that summary remains valid as bandwidth and regularization change. The manuscript develops training-derived tests that certify agreement across continuous parameter regions, identify strict exclusions with finite disagreement thresholds, and certify local bandwidth bands.'),
('body','The two-dataset evaluation covers five seeds, three prototype budgets and 2,880 archived readouts. It establishes the measured reach of the guarantees: every validation-competitive readout under the primary rule has zero full-width sufficient coverage, finite penalty paths exhibit returns to agreement, and class-conditioned comparisons explain accuracy within certified subsets. The revised literature synthesis connects this question to finite-scale identity of nearest-neighbour and exponential-potential rules and to regularization-path guarantees.'),
('body','The complete supplement preserves the training evidence, protocols, per-query records, reproducible analyses and independent numerical verification. The manuscript contains the original mathematical results, seven figures and twelve tables.'),
('body','Thank you for considering the work.'),('body','Meshaal Mouawad\nDepartment of Electrical and Computer Engineering\nMississippi State University\nmm4922@msstate.edu')]
document(cover,JF,'Cover_Letter_Neural_Networks_R5')
old=OUT/'RBF_Neural_Networks_R4/journal_files'
for n in ['Title_Page.docx','Title_Page.pdf','Declaration_of_Competing_Interest.docx','Declaration_of_Competing_Interest.pdf']:shutil.copy2(old/n,JF/n)
shutil.copy2(old/'Highlights_Neural_Networks_R4.txt',JF/'Highlights_Neural_Networks_R5.txt')
shutil.copy2(S/'main.pdf',JF/'RBF_Neural_Networks_Manuscript_R5.pdf')
shutil.copy2(supp,JF/supp.name)

for p in S.iterdir():
    if p.suffix in {'.tex','.bib','.bbl','.cls','.bst','.dtx','.ins','.svg','.png'} or (p.suffix=='.pdf' and p.name!='main.pdf'):shutil.copy2(p,STAGE/p.name)
(STAGE/'README.md').write_text('''# Integrated R5 LaTeX manuscript

Target: Neural Networks. Editorial revision of verified R4 science.
Transfer/submission is pending. All equations, experiments and result inputs
are preserved. The revised manuscript contains 40 pages, 7 figures, 12 tables
and 18 references. The abstract and introduction explain the problem before
the technical construction; the literature review and conclusion are aligned.

Compile from this directory with a standard TeX Live installation:

    latexmk -pdf -interaction=nonstopmode -halt-on-error main.tex

The complete unchanged Supplementary_Research_Artifacts_R4.zip supplies the
numerical evidence, saved models, scripts, results and independent verifiers.
Its R4 filename identifies the frozen scientific version used by R5.
SHA256_MANIFEST.json covers every other delivered source file.
''')
manifest(STAGE);archive(STAGE,JF/'LaTeX_Source_Neural_Networks_R5.zip')
shutil.copy2(OUT/'RBF_Neural_Networks_R4/verify_package.py',PKG/'verify_package.py')
(PKG/'README.md').write_text('''# RBF Neural Networks: integrated R5 revision

Start with journal_files/RBF_Neural_Networks_Manuscript_R5.pdf.
The opening, literature synthesis and conclusion are revised in LaTeX.
The scientific evidence is preserved from verified R4. No new model was fitted.

Contents:
- journal_files/: compiled manuscript, self-contained LaTeX ZIP, complete
  unchanged R4 numerical supplement, draft cover letter, highlights, title
  page and competing-interest declaration.
- revision_record/: R5 revision report, differences, primary-source and
  independent reader reviews, exact preservation checks, fresh compilation
  and PDF inspection records, and the completed A-I research plan/audits.

Verify the delivered bytes with: python verify_package.py
Extract the LaTeX ZIP and follow its README.md to rebuild the manuscript.
Extract Supplementary_Research_Artifacts_R4.zip and follow README_R4.md to
replay the saved-data analyses. The R4 filename deliberately identifies
the unchanged scientific evidence used in this R5 editorial version.

The existing GitHub repository preserves the research and receives the R5
reading version and source; the exact recorded scope is in GITHUB_R5.json.
The work is ready for independent review. Journal transfer/submission remains
pending. R5 does not change the R4 independent scientific assessment.
''')
js(ROOT/'r5_editorial/STAGED.json',{'status':'STAGED','date':DATE,'pages':pages,'abstract_words':word_count,'source_sha256':sha(S/'main.tex'),'pdf_sha256':sha(S/'main.pdf'),'source_zip_sha256':sha(JF/'LaTeX_Source_Neural_Networks_R5.zip'),'supplement_sha256':supp_hash,'package':str(PKG)})
print(json.dumps({'status':'STAGED','date':DATE,'pages':pages,'abstract_words':word_count,'report_pages':len(fitz.open(REC/'RBF_Neural_Networks_Revision_Report_R5.pdf')),'cover_pages':len(fitz.open(JF/'Cover_Letter_Neural_Networks_R5.pdf'))}))
