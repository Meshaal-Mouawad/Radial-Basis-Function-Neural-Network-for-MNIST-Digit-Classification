from pathlib import Path
import hashlib, json, re, shutil, zipfile
from datetime import datetime, timezone
from xml.sax.saxutils import escape
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, KeepTogether
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_LEFT
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import fitz

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / 'r5_gap_audit'
OUT = ROOT / 'output/RBF_R5_Research_Gap_Audit_2026-11-15'
OUT.mkdir(parents=True, exist_ok=True)
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
baseline = json.loads((ROOT/'output/RBF_Neural_Networks_R5/revision_record/FINAL_HANDOFF.json').read_text())
assert sha(ROOT/'working_R5/source/main.tex') == baseline['main_sha256']
assert sha(ROOT/'working_R5/source/main.pdf') == baseline['pdf_sha256']
assert sha(ROOT/'working_R5/source/references.bib') == '4d3d47cb7b9f28e5f83ad2fdc7e2b5b3d310abd7ae393bdb9d29f2ac483eb076'
assert sha(ROOT/'upload/Mouawad_Methodology_Research_Gap_Discovery_v1(2).md') == sha(ROOT/'project_sources/05-Mouawad_Methodology_Research_Gap_Discovery_v1.md')
ledger = json.loads((SRC/'search_ledger.json').read_text())
assert sum(len(q['queries']) for q in ledger['queries']) == ledger['coverage']['actual_queries'] == 47
assert len(ledger['records']) == 18
for name in ['RBF_R5_Research_Gap_Audit.md','frontier_challenge.md','search_ledger.json','root_search_ledger.json','build_gap_delivery.py']:
    shutil.copy2(SRC/name, OUT/name)
shutil.copy2(ROOT/'project_sources/05-Mouawad_Methodology_Research_Gap_Discovery_v1.md', OUT/'applied_methodology.md')
inherited = OUT/'inherited_verification'
inherited.mkdir(exist_ok=True)
for name in ['literature_verification.md','literature_verification.json','source_revision_consistency.md','source_revision_consistency.json','cold_reader.md','cold_reader.json']:
    shutil.copy2(ROOT/'r5_editorial/review'/name, inherited/name)
for name in ['plan_audit.json','scientific_review.json','scientific_review.md','claim_to_evidence.csv']:
    shutil.copy2(ROOT/'r4_closure'/name, inherited/name)
shutil.copy2(ROOT/'output/RBF_Neural_Networks_R5/revision_record/FINAL_HANDOFF.json', inherited/'R5_FINAL_HANDOFF.json')

fontdir=Path('/usr/share/fonts/truetype/dejavu')
pdfmetrics.registerFont(TTFont('AuditSans', str(fontdir/'DejaVuSans.ttf')))
pdfmetrics.registerFont(TTFont('AuditSansBold', str(fontdir/'DejaVuSans-Bold.ttf')))
pdfmetrics.registerFontFamily('AuditSans', normal='AuditSans', bold='AuditSansBold', italic='AuditSans', boldItalic='AuditSansBold')
styles=getSampleStyleSheet()
styles.add(ParagraphStyle(name='AuditBody',fontName='AuditSans',fontSize=9.2,leading=13,spaceAfter=7,textColor=colors.HexColor('#263442')))
styles.add(ParagraphStyle(name='AuditH1',fontName='AuditSansBold',fontSize=19,leading=24,spaceAfter=16,textColor=colors.HexColor('#183e54')))
styles.add(ParagraphStyle(name='AuditH2',fontName='AuditSansBold',fontSize=12,leading=16,spaceBefore=12,spaceAfter=8,keepWithNext=True,textColor=colors.HexColor('#183e54')))
styles.add(ParagraphStyle(name='AuditCell',fontName='AuditSans',fontSize=8.1,leading=11,spaceAfter=0))
styles.add(ParagraphStyle(name='AuditHeadCell',fontName='AuditSansBold',fontSize=8.1,leading=11,textColor=colors.white))

def inline(s):
    s=escape(s)
    s=re.sub(r'\*\*(.+?)\*\*',r'<b>\1</b>',s)
    s=re.sub(r'`([^`]+)`',r'\1',s)
    s=re.sub(r'\[([^\]]+)\]\((https?://[^)]+)\)',r'<link href="\2" color="#235d78">\1</link>',s)
    # Display DOIs as compact identifiers; make the complete report URLs clickable.
    s=re.sub(r'(?<!["=])(https?://[^\s<]+)',lambda m:'<link href="'+m.group(1)+'" color="#235d78">'+m.group(1)+'</link>',s)
    return s

lines=(OUT/'RBF_R5_Research_Gap_Audit.md').read_text().splitlines()
flow=[]; i=0
while i<len(lines):
    line=lines[i].strip()
    if not line: i+=1; continue
    if line.startswith('|'):
        rows=[]
        while i<len(lines) and lines[i].strip().startswith('|'):
            cells=[c.strip() for c in lines[i].strip().strip('|').split('|')]
            if not all(re.fullmatch(r':?-+:?',c) for c in cells): rows.append(cells)
            i+=1
        n=len(rows[0]); widths=([114,184,201] if n==3 else [90,116,195,98])
        data=[[Paragraph(inline(c),styles['AuditHeadCell' if k==0 else 'AuditCell']) for c in row] for k,row in enumerate(rows)]
        t=Table(data,colWidths=widths,repeatRows=1,hAlign='LEFT')
        t.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,0),colors.HexColor('#244b60')),('VALIGN',(0,0),(-1,-1),'TOP'),('LEFTPADDING',(0,0),(-1,-1),7),('RIGHTPADDING',(0,0),(-1,-1),7),('TOPPADDING',(0,0),(-1,-1),7),('BOTTOMPADDING',(0,0),(-1,-1),7),('ROWBACKGROUNDS',(0,1),(-1,-1),[colors.HexColor('#eef3f5'),colors.white]),('LINEBELOW',(0,0),(-1,0),0.4,colors.HexColor('#244b60')),('LINEBELOW',(0,1),(-1,-1),0.3,colors.HexColor('#d8e1e5'))]))
        flow += [t,Spacer(1,9)]
        continue
    if line.startswith('# '): flow.append(Paragraph(inline(line[2:]),styles['AuditH1'])); i+=1; continue
    if line.startswith('## '): flow.append(Paragraph(inline(line[3:]),styles['AuditH2'])); i+=1; continue
    if line.startswith('- '): flow.append(Paragraph('• '+inline(line[2:]),styles['AuditBody'])); i+=1; continue
    para=[line]; i+=1
    while i<len(lines) and lines[i].strip() and not lines[i].startswith(('#','|','- ')):
        para.append(lines[i].strip()); i+=1
    flow.append(Paragraph(inline(' '.join(para)),styles['AuditBody']))

pdf=OUT/'RBF_R5_Research_Gap_Audit.pdf'
def page(c,doc):
    c.setFont('AuditSans',7.5);c.setFillColor(colors.HexColor('#61717c'))
    c.drawString(48,810,'RBF R5  |  Research-gap verification  |  15 November 2026')
    c.drawString(48,27,'Prepared for Dr. Meshaal Mouawad')
    c.drawRightString(547,27,str(doc.page))
SimpleDocTemplate(str(pdf),pagesize=(595,842),leftMargin=48,rightMargin=48,topMargin=50,bottomMargin=48,title='RBF R5 research-gap audit',author='Meshaal Mouawad').build(flow,onFirstPage=page,onLaterPages=page)
doc=fitz.open(pdf)
render=ROOT/'tmp/r5_gap_pdf_review'; render.mkdir(parents=True,exist_ok=True)
for idx,p in enumerate(doc): p.get_pixmap(matrix=fitz.Matrix(1.2,1.2),alpha=False).save(render/f'page-{idx+1:02}.png')
decision={
 'status':'RESEARCH_GAP_AUDIT_COMPLETE','editorial_recommendation':'READY_TO_DRAFT_WITH_VERIFIED_EVIDENCE',
 'existing_manuscript_action':'PROCEED_TO_INDEPENDENT_REVIEW_WITH_R5',
 'gap_verdict':'CONFIRMED_WITHIN_VERIFIED_SEARCH_SCOPE','manuscript_revision_required':False,
 'new_training_runs':0,'new_numerical_pipeline_runs':0,
 'new_query_batches':13,'new_queries':47,'curated_papers':18,'target_journal_records':7,
 'count_scope':'Independent frontier ledger only; complementary root searches separately recorded',
 'search_date_local':'2026-11-15','timezone':'Asia/Riyadh','utc_date':'2026-11-14',
 'finalized_utc':datetime.now(timezone.utc).isoformat(),
 'gates':{f'J{x}':('PASS_WITHIN_RECORDED_SEARCH_SCOPE' if x in [1,2,5] else 'PASS_AT_RECORDED_ACCESS_LEVELS' if x==9 else 'PASS') for x in range(1,11)},
 'scientific_significance_prior_assessment':'BORDERLINE','journal_transfer_submission_complete':False,
 'manuscript_sha256':sha(ROOT/'working_R5/source/main.tex'),'manuscript_pdf_sha256':sha(ROOT/'working_R5/source/main.pdf'),
 'bibliography_sha256':sha(ROOT/'working_R5/source/references.bib'),
 'baseline_github_commit':'059e0204c1fee7b52bae744cda65a7e0b7399d1c',
 'report_pages':len(doc),'report_visual_inspection':'PENDING',
 'configured_search_agent':{'model':'gpt-6.1-sol','reasoning':'high','fork_turns':'none'},
 'access_gaps':['GNPC1998 primary scientific body','Sun and Wang review reference chain','Lin2024 body','Recent peripheral target-journal full bodies'],
 'unresolved_mandatory_manuscript_fixes':[]}
(OUT/'AUDIT_DECISION.json').write_text(json.dumps(decision,indent=2)+'\n')
print(json.dumps({'report':str(pdf),'pages':len(doc),'render_directory':str(render),'manuscript_unchanged':True}))
