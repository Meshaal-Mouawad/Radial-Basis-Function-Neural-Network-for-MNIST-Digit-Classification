"""Build the integrated R4 delivery; clean-extraction gates finalize separately."""
from pathlib import Path
import csv,difflib,hashlib,json,re,shutil,sys,zipfile
import fitz,numpy,scipy,threadpoolctl
from xml.sax.saxutils import escape
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet,ParagraphStyle
from reportlab.platypus import SimpleDocTemplate,Paragraph,Spacer,Table,TableStyle,PageBreak
ROOT=Path(__file__).resolve().parents[2];OUT=ROOT/'output';PKG=OUT/'RBF_Neural_Networks_R4';JF=PKG/'journal_files';REC=PKG/'revision_record';S=ROOT/'working_R4/source';OLD=OUT/'RBF_Neural_Networks_R3';BASE=ROOT/'baseline_source';STAGE=ROOT/'tmp/r4_delivery'
for p in [JF,REC,PKG/'preserved_R3',STAGE]:p.mkdir(parents=True,exist_ok=True)
def sha(p):
 h=hashlib.sha256()
 with Path(p).open('rb') as f:
  for b in iter(lambda:f.read(1048576),b''):h.update(b)
 return h.hexdigest()
def js(p,o):Path(p).write_text(json.dumps(o,indent=2)+'\n')
def files(p):return sorted(x for x in Path(p).rglob('*') if x.is_file() and '__pycache__' not in x.parts)
def manifest(p):js(p/'SHA256_MANIFEST.json',{str(x.relative_to(p)):sha(x) for x in files(p) if x!=p/'SHA256_MANIFEST.json'})
def archive(p,dest):
 with zipfile.ZipFile(dest,'w',zipfile.ZIP_DEFLATED,compresslevel=6) as z:
  for x in files(p):z.write(x,str(x.relative_to(p)))
styles=getSampleStyleSheet()
for name,size,leading,color in [('TitleR4',20,24,'#193449'),('HeadR4',12,16,'#193449'),('BodyR4',10,13.5,'#182a38'),('SmallR4',8.8,11.5,'#52616d'),('CellR4',9,11.5,'#182a38')]:
 styles.add(ParagraphStyle(name=name,fontName='Helvetica-Bold' if name.startswith(('Title','Head')) else 'Helvetica',fontSize=size,leading=leading,textColor=colors.HexColor(color),spaceAfter=8,spaceBefore=6 if name=='HeadR4' else 0))
def para(t,style):return Paragraph(escape(str(t)).replace('\n','<br/>'),style)
def footer(c,doc):
 c.setStrokeColor(colors.HexColor('#c7d2da'));c.line(48,42,564,42);c.setFont('Helvetica',8);c.setFillColor(colors.HexColor('#52616d'));c.drawString(48,29,'RBF / Neural Networks / R4 / 14 November 2026');c.drawRightString(564,29,str(doc.page))
def render(blocks,path):
 story=[]
 for k,x in blocks:
  if k=='page':story.append(PageBreak())
  elif k=='table':
   data,widths=x;t=Table([[para(c,styles['CellR4']) for c in row] for row in data],colWidths=widths,repeatRows=1,hAlign='LEFT');t.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,0),colors.HexColor('#e8eff4')),('VALIGN',(0,0),(-1,-1),'TOP'),('LINEBELOW',(0,0),(-1,0),.7,colors.HexColor('#667d8e')),('LINEBELOW',(0,-1),(-1,-1),.6,colors.HexColor('#b4c2cb')),('LEFTPADDING',(0,0),(-1,-1),6),('RIGHTPADDING',(0,0),(-1,-1),6),('TOPPADDING',(0,0),(-1,-1),6),('BOTTOMPADDING',(0,0),(-1,-1),6)]));story.extend([t,Spacer(1,8)])
  else:story.append(para(x,styles[{'title':'TitleR4','h':'HeadR4','p':'BodyR4','small':'SmallR4'}[k]]))
 SimpleDocTemplate(str(path),pagesize=(612,792),rightMargin=48,leftMargin=48,topMargin=46,bottomMargin=58,title=path.stem.replace('_',' '),author='Meshaal Mouawad').build(story,onFirstPage=footer,onLaterPages=footer)
def md(blocks):
 out=[]
 for k,x in blocks:
  if k in ['title','h']:out.append(('# ' if k=='title' else '## ')+x)
  elif k in ['p','small']:out.append(x)
  elif k=='table':
   rows=x[0];out.append('\n'.join(['| '+' | '.join(rows[0])+' |','| '+' | '.join(['---']*len(rows[0]))+' |']+['| '+' | '.join(row)+' |' for row in rows[1:]]))
 return '\n\n'.join(out)+'\n'
def document(blocks,folder,stem):
 (folder/(stem+'.md')).write_text(md(blocks));render(blocks,folder/(stem+'.pdf'))

# Protect every original scientific object.
a=(BASE/'main.tex').read_text();b=(S/'main.tex').read_text();protected=['results.tex','frontier_results.tex','ridge_theory.tex','exact_ridge_examples.tex','references.bib']+[p.name for p in sorted(BASE.glob('Figure*.pdf'))]
checks={n:sha(BASE/n)==sha(S/n) for n in protected};env={}
for name in ['equation','theorem','lemma','proposition','proof']:
 pat=r'\\begin\{'+name+r'\}.*?\\end\{'+name+r'\}';x=re.findall(pat,a,re.S);y=re.findall(pat,b,re.S);env[name]={'count':len(x),'exact':x==y}
declaration='During preparation of this work, the author used Elsevier LeapSpace, other tools to support literature discovery, manuscript organization, language refinement, and consistency checking. The authors take responsibility for the content of the article.'
assert all(checks.values()) and all(x['exact'] for x in env.values());assert a.count(declaration)==b.count(declaration)==1
oldhash=json.loads((ROOT/'r4_analysis/integration/R3_BASELINE_HASHES.json').read_text())
# Keys in the checkpoint are R3 source basenames.
for n,h in oldhash.items():assert sha(ROOT/'working_R3/source'/n)==h,n
D=fitz.open(S/'main.pdf');pdftext='\n'.join(p.get_text() for p in D);assert len(D)==41;assert 'Appendix Appendix' not in pdftext and '(??)' not in pdftext
bad=[x for x in (S/'main.log').read_text().splitlines() if any(k in x for k in ['Overfull','Underfull','undefined','multiply defined'])];assert not bad,bad
js(REC/'PROTECTION_AND_PDF_AUDIT.json',{'status':'PASS','pages':41,'figures':7,'tables':12,'bibliography_entries':len(re.findall(r'\\bibitem',(S/'main.bbl').read_text())),'protected_R2_files':checks,'protected_main_math':env,'approved_AI_declaration_exact':True,'R3_baseline_hashes_unchanged':True,'layout_reference_warnings':bad,'pdf_sha256':sha(S/'main.pdf'),'inspection':'All 41 pages inspected in contact sheets; new pages 31–34 individually inspected at full scale. No clipped labels, overflows, unreadable tables or unresolved references.'})
for stem in ['composition','competitive','paths_efficiency','summary_tables']:assert json.loads((ROOT/f'r4_analysis/independent/{stem}_verification.json').read_text())['status']=='PASS'

diff=[]
for n in ['main.tex','r4_methods.tex','r4_results.tex','r4_composition_table.tex','r4_paths_table.tex','r4_competitive_table.tex','r4_probe_table.tex']:
 before=ROOT/'working_R3/source'/n;diff.extend(difflib.unified_diff(before.read_text().splitlines(True) if before.exists() else [],(S/n).read_text().splitlines(True),fromfile='R3/'+n,tofile='R4/'+n))
(REC/'R3_to_R4.diff').write_text(''.join(diff))

report=[('title','R4 integrated revision report'),('small','14 November 2026 | Neural Networks transfer preparation | Meshaal Mouawad'),('h','Completed manuscript'),('p','R4 implements the approved saved-data analyses directly in the LaTeX manuscript. The compiled manuscript has 41 pages, seven figures, twelve tables, and 17 references. The six original figures, mathematical results and approved AI declaration are preserved. No new model was fitted.'),('h','Research changes and locations'),('table',([
 ['Analysis','Finding integrated','Location'],['C: class composition','Class-balanced accuracy, retention, accepted recall, effective class count and exact selected-set overlap.','Sections 5.7, 6.10; Table 9; Figure 7'],['D: finite paths','Observed first disagreement, sampled return to agreement, sign changes and comparison with sufficient tail bounds.','Sections 5.8, 6.11; Table 10'],['E: competitive operation','All 30 groups and all 2,880 archived pairs; validation-selected models and 90/95/99% competitive sets.','Sections 5.9, 6.12; Table 11'],['F: exclusion accumulation','All seven K=100 widths and three floors, using fixed-order original and expanded finite probes.','Sections 5.8, 6.13; Table 12'],['G: stability','All paired seed results, budget gains, class counts, prediction disagreement and correct-set overlap.','Sections 5.9, 6.12; supplement']],[96,314,106])),('p','The abstract and introduction state the actual analytical contribution and measured reach. Discussion distinguishes persistence over continuous families, finite-model accuracy, selected-set composition, and observed regularization paths. The single end Limitations section consolidates empirical scope and boundary conditions.'),('page',''),('title','Verified findings'),('h','Competitive operation and stability'),('p','The primary 95%-of-best-validation rule retains 328 models across the 30 groups; every retained model has zero sharp full-width certificate coverage. The 90% and 99% sensitivity sets retain 494 and 116 models with the same zero result. All 30 best-validation models choose zero penalty.'),('table',([
 ['Dataset','K=50 accuracy (%)','K=100 accuracy (%)','K=200 accuracy (%)'],['MNIST','82.92 ± 0.46','88.43 ± 0.27','91.80 ± 0.31'],['Fashion-MNIST','76.23 ± 0.88','79.38 ± 0.63','82.13 ± 0.19']],[132,128,128,128])),('p','Accuracy improves at every budget step in every seed. Paired K=50 to K=200 gains are 8.88 ± 0.41 percentage points for MNIST and 5.90 ± 0.80 for Fashion-MNIST. Across the ten seed pairs, prediction disagreement falls from 14.29% to 5.95% and from 12.21% to 8.15%, respectively. Region exclusion is defined separately from endpoint error.'),('h','Finite-path behavior and exclusions'),('p','The exhaustive path reconstruction finds 190,405 returns to strict agreement among 3,366,480 query–width paths. Up to five sign changes occur across six sampled penalties. Sufficient tail bounds remain distinct from observed early disagreement and later agreement.'),('p','At t=sC and floor zero, the expanded finite archive recovers 95% of the original limiting-witness cases after mean 15.6 checks on MNIST and 20.2 on Fashion-MNIST, in every seed. The original finite archive never reaches that target in the ten groups. These are fixed-order archived-check counts.'),('h','Composition of selected subsets'),('p','At the MNIST constant class-1 endpoint, all ten true classes remain represented in the certified subset: selected-class macro accuracy is 10%, despite 68.93% micro accuracy. For Fashion-MNIST at t=sC, gated-distance selection raises selected-class macro accuracy from 25.49% to 44.21% and effective predicted classes from 1.71 to 3.73. The two sets have mean Jaccard 0.313 at equal cardinality.'),('page',''),('title','Verification and delivery'),('h','Independent numerical reconstruction'),('table',([
 ['Audit','Verified evidence'],['C composition','20 settings, 40 selector rows, 400 class records, 140,270 prediction labels'],['D/F paths and probes','20,198,880 labels; 3,366,480 paths; 480 width summaries; 70 bound rows; 1,161 finite masks; 21,630 cumulative rows; 420 region summaries'],['E/G competitive models','14.4 million validation labels; 20,198,880 evaluation labels; 2,880 independently computed masks; 630 original masks; all summary tables'],['Source/PDF protection','Original protected bytes and math exact; R3 checkpoint unchanged; 41 pages inspected; no layout or cross-reference warnings']],[142,374])),('p','The numerical verifier implements sharp certificates directly from the equations and replays raw images with archived weights. It does not import the production runners or the frozen certificate implementation. The separate source/evidence review and clean-extraction receipts are retained in revision_record/.'),('h','Package and reproducibility'),('p','journal_files/ contains the compiled PDF, standalone LaTeX ZIP, complete numerical supplement, revised draft cover letter, highlights, title page and competing-interest files. revision_record/ contains this report, the one-page decision summary, source diff, scientific reviews, build and fresh-extraction checks. preserved_R3/ retains the preceding PDF and source ZIP.'),('p','The supplement preserves the complete original R2 evidence and R3 analyses, then adds the adopted plan, composition records, R4 protocols, full arrays, CSVs, plots and four independent verifiers. Its README documents hash verification and fresh reconstruction. The source ZIP compiles independently. Every archive is checked against a SHA-256 manifest.'),('h','Readiness and editorial decision'),('p','Internal review readiness is determined by completed analyses, preservation, independent reconstruction, compilation, page inspection and clean-extraction checks. REVIEW_READY.json records those gates and final hashes after all checks pass. This is an internal manuscript version. The Neural Networks transfer/submission process remains incomplete.'),('h','Limitations and significance'),('p','The requested analyses are complete. They establish zero competitive full-width coverage, observed nonmonotone paths and exact composition/overlap behavior in the archived model families. Predictive or model-selection benefit and measured computational speedup are not established. The editor’s broader significance judgment remains unresolved. Current portal-specific requirements require checking during submission; no journal submission was performed.')]
document(report,REC,'RBF_Neural_Networks_Revision_Report_R4')
decision=[('title','R4 decision summary'),('small','14 November 2026 | Internal author review | Neural Networks transfer pending'),('h','Decision'),('p','Release the integrated R4 manuscript for author review after the recorded production gates pass. All approved saved-data analyses are implemented. The editor’s significance concern remains unresolved.'),('table',([
 ['Question','Evidence and conclusion'],['Does coverage reach competitive models?','No. All 328 models retained by the primary 95% validation rule have zero sharp full-width coverage. The 90% and 99% sets give the same outcome.'],['Does agreement change monotonically with penalty?','No. 190,405 of 3,366,480 sampled query–width paths return to strict agreement; some alternate at all six penalties.'],['What explains selected-subset accuracy?','Class composition matters. At the MNIST constant class-1 endpoint, macro selected-class accuracy is 10% across ten represented classes.'],['What do limiting witnesses add?','Expanded archived probes recover 95% of their cases after mean 15.6 / 20.2 checks at t=sC; exact residual exclusions remain recorded.']],[172,344])),('h','Completed checks'),('p','Independent numerical reconstruction passed for C–G. The 41-page PDF contains seven figures and twelve tables. The six original figures, original mathematics, evidence and AI declaration are preserved. Clean-extraction and final hash receipts accompany the package.'),('h','Next decision'),('p','The research now has an exhaustive account of the guarantees’ reach in the archived models. Decide whether this demonstrated analytical contribution addresses the journal’s impact standard. Neural Networks transfer/submission remains incomplete; no manuscript has been submitted by this workflow.')]
document(decision,REC,'RBF_Neural_Networks_R4_Decision_Summary')
assert len(fitz.open(REC/'RBF_Neural_Networks_R4_Decision_Summary.pdf'))==1
cover=[('title','Transfer manuscript: Neural Networks'),('small','14 November 2026 | Draft cover letter'),('p','Dear Editor,'),('p','Please consider Training-Derived Regions of Nearest-Prototype Agreement in Gaussian RBF Classifiers as a research article. The manuscript was previously submitted to Neurocomputing under NEUCOM-D-26-25836; I selected Neural Networks for the proposed transfer.'),('p','The work develops training-derived conditions for agreement with a nearest-prototype label throughout Gaussian ridge RBF parameter regions. Its mathematical results certify continuous bandwidth–penalty regions, identify strict large-penalty exclusions with finite disagreement bounds, and certify local bandwidth bands with penalty tails.'),('p','This integrated revision exhaustively examines the original 30 dataset–seed–budget groups. It quantifies zero full-width coverage among validation-competitive readouts, nonmonotone agreement along finite regularization paths, class composition within matched selected subsets, and the accumulation of finite exclusions relative to analytical witnesses. These results establish the measured reach of continuous decision-persistence guarantees in the studied model families.'),('p','The original evidence, proofs and six figures are preserved. The manuscript adds a class-specific figure and four new tables to the preceding integrated version. The complete supplement retains protocols, per-query arrays, reproducible scripts, hashes, and independent numerical reconstruction.'),('p','Thank you for considering the work.'),('p','Meshaal Mouawad\nDepartment of Electrical and Computer Engineering\nMississippi State University\nmm4922@msstate.edu')]
document(cover,JF,'Cover_Letter_Neural_Networks_R4')
highlights=['Training-derived tests certify agreement across RBF parameter regions.','Strict limiting votes provide finite disagreement bounds.','Validation-competitive models have zero full-width sufficient coverage.','Finite penalty paths exhibit disagreement followed by renewed agreement.','Class-balanced diagnostics resolve the composition of certified subsets.'];assert all(len(x)<=85 for x in highlights)
(JF/'Highlights_Neural_Networks_R4.txt').write_text('\n'.join('- '+x for x in highlights)+'\n')
for n in ['Title_Page.docx','Title_Page.pdf','Declaration_of_Competing_Interest.docx','Declaration_of_Competing_Interest.pdf']:shutil.copy2(OLD/'journal_files'/n,JF/n)
shutil.copy2(S/'main.pdf',JF/'RBF_Neural_Networks_Manuscript_R4.pdf')
for n in ['RBF_Neural_Networks_Manuscript_R3.pdf','LaTeX_Source_Neural_Networks_R3.zip']:shutil.copy2(OLD/'journal_files'/n,PKG/'preserved_R3'/n)
for p in (ROOT/'r4_analysis/review').glob('*.md'):shutil.copy2(p,REC/p.name)
for p in (ROOT/'r4_analysis/independent').glob('*'):
 if p.suffix in ['.md','.json','.log']:shutil.copy2(p,REC/p.name)
for p in (ROOT/'r4_analysis/integration').glob('*.py'):
 (REC/'integration_scripts').mkdir(exist_ok=True);shutil.copy2(p,REC/'integration_scripts'/p.name)
shutil.copy2(ROOT/'logs/r4_build.log',REC/'r4_build.log')
shutil.copy2(ROOT/'r4_analysis/integration/R3_BASELINE_HASHES.json',REC/'R3_BASELINE_HASHES.json')
js(REC/'INPUT_PROVENANCE.json',{'date':'2026-11-14','R3_full_archive_sha256':sha(OUT/'RBF_Neural_Networks_Full_Revision_R3_2026-11-14.zip'),'R3_full_archive_library_id':'libfile_fde3_f-71dfede02ec4819191adc1b8c63f0738_6246015f02148191b6fb1aaa7040b316','global_protocol_sha256':sha(ROOT/'r4_analysis/protocol.json'),'new_fits':0,'runtime':{'python':sys.version,'numpy':numpy.__version__,'scipy':scipy.__version__,'threadpoolctl':threadpoolctl.__version__}})
source=STAGE/'source';source.mkdir(exist_ok=True)
for p in S.iterdir():
 if p.suffix in ['.tex','.bib','.bbl','.cls','.bst','.dtx','.ins','.svg','.png'] or (p.suffix=='.pdf' and p.name!='main.pdf'):shutil.copy2(p,source/p.name)
(source/'README.md').write_text('''# Integrated R4 manuscript source

Target: Neural Networks. Internal version R4, 14 November 2026.
Transfer/submission remains incomplete.

Compile in this directory using a standard TeX installation:

    latexmk -pdf -interaction=nonstopmode -halt-on-error main.tex

The verified PDF has 41 pages, seven figures, twelve tables and 17 references.
The original six figures, theory and approved AI declaration are preserved.
R4 integrates r4_methods.tex, r4_results.tex and four r4_*_table.tex inputs.
R3's original diagnostic files remain integrated.
The companion numerical supplement supplies evidence and independent verifiers.
SHA256_MANIFEST.json covers every other file.
''')
manifest(source);archive(source,JF/'LaTeX_Source_Neural_Networks_R4.zip')
supp=STAGE/'supplement';supp.mkdir(exist_ok=True)
with zipfile.ZipFile(OLD/'journal_files/Supplementary_Research_Artifacts_R3.zip') as z:z.extractall(supp)
for folder in ['competitive','disagreement','composition','independent']:
 for p in files(ROOT/'r4_analysis'/folder):
  dest=supp/'r4_analysis'/folder/p.relative_to(ROOT/'r4_analysis'/folder);dest.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,dest)
(supp/'r4_analysis/integration').mkdir(exist_ok=True)
shutil.copy2(ROOT/'r4_analysis/integration/build_composition.py',supp/'r4_analysis/integration/build_composition.py')
shutil.copy2(ROOT/'r4_analysis/protocol.json',supp/'r4_analysis/protocol.json')
for p in files(ROOT/'next_work'):
 dest=supp/'next_work'/p.relative_to(ROOT/'next_work');dest.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,dest)
(supp/'README_R4.md').write_text('''# R4 complete numerical supplement

Extract into an empty directory. Keep evidence/, r3_analysis/, r4_analysis/,
and next_work/ together. evidence/ is the complete unchanged R2 evidence;
r3_analysis/ preserves the preceding numerical diagnostics. R4 performs no fits.

Verify delivered bytes first:

    python verify_package.py

In a disposable extracted copy, independently reconstruct C–G:

    PYTHONDONTWRITEBYTECODE=1 python r4_analysis/independent/verify_composition.py
    PYTHONDONTWRITEBYTECODE=1 python r4_analysis/independent/verify_competitive.py
    PYTHONDONTWRITEBYTECODE=1 python r4_analysis/independent/verify_paths_efficiency.py
    PYTHONDONTWRITEBYTECODE=1 python r4_analysis/independent/verify_summary_tables.py

These scripts refresh their adjacent verification JSONs; the delivered originals
remain authoritative records. Script outputs may have different runtimes.
Use README_R3.md for the earlier diagnostic and original R2 reconstruction.

For full R4 regeneration from archived weights, still without training:

    python next_work/analyze_saved_selections.py
    python r4_analysis/competitive/run_competitive.py --evidence evidence
    python r4_analysis/competitive/make_plots.py
    python r4_analysis/disagreement/run_saved_paths.py --recompute

The competitive runner resumes only valid matching checkpoints. To force fresh
output use its --output option in a disposable copy. Consult each frozen
protocol and REPORT.md for choices, denominators, numerical guards and scope.
To regenerate the composition plots, extract the companion LaTeX source into
working_R4/source/ beside this tree, then run:

    python r4_analysis/integration/build_composition.py

Python 3.12; NumPy 2.3.5; SciPy 1.17.0; threadpoolctl 3.6.0; Matplotlib required.
No paid compute, new fits or journal submission is part of these commands.
''')
(supp/'requirements_R4.txt').write_text('numpy==2.3.5\nscipy==1.17.0\nthreadpoolctl==3.6.0\nmatplotlib\n')
manifest(supp);archive(supp,JF/'Supplementary_Research_Artifacts_R4.zip')
shutil.copy2(OLD/'verify_package.py',PKG/'verify_package.py')
(PKG/'README.md').write_text('''# Integrated Neural Networks R4 revision

14 November 2026. Internal author-review version; transfer/submission incomplete.
Start with journal_files/RBF_Neural_Networks_Manuscript_R4.pdf and the one-page
decision summary plus revision report in revision_record/.

journal_files/: compiled manuscript, standalone source ZIP, complete numerical
supplement, draft cover letter, highlights, title page and interest declaration.
revision_record/: independent audits, source review, production checks, source
diff, build and clean-extraction logs, and final REVIEW_READY.json gate.
preserved_R3/: unchanged preceding manuscript and source ZIP.

Verify the complete delivery with: python verify_package.py
Extract the numerical supplement and follow README_R4.md for independent replay.
Extract the source ZIP and follow its README.md to compile.

All C–G analyses use archived evidence and perform no new model fits. The six
original figures, original mathematical results and approved AI declaration are
preserved. Seven figures and twelve tables appear in the integrated manuscript.
Internal review readiness does not resolve the editor's significance decision.
''')
print(json.dumps({'status':'STAGED','pages':41,'files':len(files(PKG)),'supplement_bytes':(JF/'Supplementary_Research_Artifacts_R4.zip').stat().st_size,'source_bytes':(JF/'LaTeX_Source_Neural_Networks_R4.zip').stat().st_size,'report_pages':len(fitz.open(REC/'RBF_Neural_Networks_Revision_Report_R4.pdf'))}))
