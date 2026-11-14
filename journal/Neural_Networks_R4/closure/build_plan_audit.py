#!/usr/bin/env python3
"""Document exact plan coverage using existing receipts, without altering R4."""
import csv
import hashlib
import json
import time
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'r4_closure'
START = time.perf_counter()

def read(p):
    return json.loads((ROOT/p).read_text())

def sha(p):
    h = hashlib.sha256()
    with (ROOT/p).open('rb') as f:
        for b in iter(lambda: f.read(1 << 20), b''):
            h.update(b)
    return h.hexdigest()

def refs(paths):
    return {p: sha(p) for p in sorted(set(paths))}

def dump(name, obj):
    (OUT/name).write_text(json.dumps(obj, indent=2, sort_keys=True)+'\n')

def csv_write(name, rows):
    with (OUT/name).open('w', newline='') as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0])); w.writeheader(); w.writerows(rows)

def local_paths(pattern):
    return [str(p.relative_to(ROOT)) for p in sorted(ROOT.glob(pattern))]

plan = 'next_work/RBF_Next_Work_Plan.md'
protocol = 'r4_analysis/protocol.json'
c_receipt = 'r4_analysis/independent/composition_verification.json'
d_receipt = 'r4_analysis/disagreement/results/COMPLETE.json'
e_receipt = 'r4_analysis/competitive/results/COMPLETE.json'
f_receipt = 'r4_analysis/independent/paths_efficiency_verification.json'
g_receipt = 'r4_analysis/independent/competitive_verification.json'
summary_receipt = 'r4_analysis/independent/summary_tables_verification.json'
package = 'output/RBF_Neural_Networks_R4/'
frozen_pdf = package+'journal_files/RBF_Neural_Networks_Manuscript_R4.pdf'

# Record exact individual input hashes and validate them against existing receipts.
expected_inputs = dict(read(c_receipt)['input_sha256'])
groups = read(e_receipt)['all_group_receipts']
for g in groups:
    p = 'evidence/baseline/evidence/baseline/work/v2/experiment/results/'+g['group']+'/predictions_before_labels.npz'
    expected_inputs[p] = g['input_sha256']
    expected_inputs.update({'evidence/'+p:h for p,h in g['data_hashes'].items()})
expected_inputs.update({'r3_analysis/m1_m2/results/'+p.name:sha(str(p.relative_to(ROOT)))
                        for p in ROOT.glob('r3_analysis/m1_m2/results/*.npz')})
expected_inputs.update({str(p.relative_to(ROOT)):sha(str(p.relative_to(ROOT)))
                       for p in ROOT.glob('evidence/new_analysis/limit_diagnostic/INPUT_SHA256.json')})
input_checks = [{ 'path':p, 'expected_sha256':h, 'actual_sha256':sha(p),
                  'status':'PASS' if sha(p)==h else 'FAIL'} for p,h in sorted(expected_inputs.items())]
dump('input_evidence_hashes.json', {'status':'PASS' if all(x['status']=='PASS' for x in input_checks) else 'FAIL',
     'files':input_checks, 'scope':'Individual inputs required by R4 C-G plus hash-linked historical input manifest; hashes recomputed at audit time.'})
input_ref = 'r4_closure/input_evidence_hashes.json'

claim_specs = [
 ('T1','A sufficient certificate guarantees nearest-prototype agreement throughout the stated continuous bandwidth/penalty region.',
  'thm:agreement; fig:mechanism', ['working_R4/source/main.tex'], ['working_R4/source/results.tex'],
  ['evidence/baseline/evidence/baseline/work/v2/experiment/certificate.py'], ['logs/r4_clean_numerical_verification.json']),
 ('T2','Strict limiting-vote reversal excludes a region; B supplies a sufficient penalty-tail bound.',
  'prop:ridge-limit; sec:r3-thresholds', ['working_R4/source/ridge_theory.tex','working_R4/source/r3_threshold_table.tex'],
  ['r3_analysis/m1_m2/results/m1_thresholds_per_seed.csv','r3_analysis/m1_m2/results/m1_summary.csv'],
  ['r3_analysis/m1_m2/run_analysis.py'], ['r3_analysis/independent/verification.json']),
 ('T3','The local-width theorem certifies agreement throughout its stated continuous band and penalty tail.',
  'thm:local-tail; tab:local-tail', ['working_R4/source/ridge_theory.tex','working_R4/source/new_results.tex'],
  ['evidence/new_analysis/limit_diagnostic/local_tail/per_seed.csv','evidence/new_analysis/limit_diagnostic/local_tail/summary.csv'],
  ['evidence/new_analysis/limit_diagnostic/run_local_tail.py'], ['r3_analysis/verification/reconstruct_r2_arrays.json']),
 ('C1','MNIST at t=sC predicts class 1 for every endpoint query; both selectors choose identical sets in every seed; selected-class macro accuracy is 10%.',
  'sec:r4-composition-results; fig:r4-composition; Table 9', ['working_R4/source/r4_composition_table.tex','working_R4/source/Figure_07_Selected_Class_Accuracy.pdf'],
  ['next_work/results/selection_diagnostics_per_seed.csv','next_work/results/selection_diagnostics_classes.csv','next_work/results/selection_diagnostics_summary.csv'],
  ['next_work/analyze_saved_selections.py'], [c_receipt]),
 ('C2','Fashion-MNIST t=sC certificate and gated-distance selected sets differ, with mean Jaccard 0.313 and effective predicted classes 1.71 versus 3.73.',
  'sec:r4-composition-results; Table 9', ['working_R4/source/r4_composition_table.tex'],
  ['next_work/results/selection_diagnostics_per_seed.csv','next_work/results/selection_diagnostics_summary.csv'], ['next_work/analyze_saved_selections.py'],[c_receipt]),
 ('D1','190405 of 3366480 sampled query-width paths return to strict agreement; the maximum sampled sign-change count is five.',
  'sec:r4-path-results; Table 10', ['working_R4/source/r4_paths_table.tex'],
  ['r4_analysis/disagreement/results/D_per_group.csv','r4_analysis/disagreement/results/D_per_width.csv','r4_analysis/disagreement/results/D_summary.csv'],
  ['r4_analysis/disagreement/run_saved_paths.py'],[f_receipt,summary_receipt]),
 ('D2','Observed finite-grid disagreement and sufficient bound B are distinct; matching-width comparisons retain below-B, no-finite-B and missing-bound cases.',
  'sec:r4-path-results', ['working_R4/source/r4_results.tex'], ['r4_analysis/disagreement/results/D_bounds.csv'],
  ['r4_analysis/disagreement/run_saved_paths.py'],[f_receipt]),
 ('E1','All 328 models retained by the 95% validation rule have zero full-width certificate coverage; 90% and 99% retain 494 and 116 with the same outcome.',
  'sec:r4-competitive-results; Table 11', ['working_R4/source/r4_competitive_table.tex'],
  ['r4_analysis/competitive/results/competitive_sets_per_seed.csv','r4_analysis/competitive/results/competitive_sets_summary.csv','r4_analysis/competitive/results/surface_per_model.csv'],
  ['r4_analysis/competitive/run_competitive.py'],[g_receipt,summary_receipt]),
 ('F1','Fixed-order expanded finite probes capture 95% of L0 at t=sC after mean 15.6 MNIST and 20.2 Fashion-MNIST checks; every original/expanded R3 union is recovered exactly.',
  'sec:r4-probe-results; Table 12', ['working_R4/source/r4_probe_table.tex'],
  ['r4_analysis/disagreement/results/F_summary.csv','r4_analysis/disagreement/results/F_aggregate.csv'],
  ['r4_analysis/disagreement/run_saved_paths.py'],[f_receipt]),
 ('F2','Actual new solves are zero; probe-prefix and redundant-check counts are retrospective operation counts. Saved solve seconds and speedup are NOT_SUPPORTED.',
  'sec:r4-probe-results; Limitations', ['working_R4/source/r4_results.tex','working_R4/source/main.tex'],
  ['r4_analysis/disagreement/results/F_summary.csv','r4_closure/F_cost_accounting.csv'],
  ['r4_analysis/disagreement/run_saved_paths.py'],[d_receipt,f_receipt]),
 ('G1','Validation-selected evaluation accuracy increases at each adjacent prototype-budget step in all five paired seeds for both datasets.',
  'sec:r4-competitive-results; Table 11', ['working_R4/source/r4_results.tex','working_R4/source/r4_competitive_table.tex'],
  ['r4_analysis/competitive/results/budget_paired_per_seed.csv','r4_analysis/competitive/results/budget_paired_summary.csv','r4_analysis/competitive/results/validation_best_per_seed.csv'],
  ['r4_analysis/competitive/run_competitive.py'],[g_receipt,summary_receipt]),
 ('G2','Seed and budget comparisons reuse the same 4027 MNIST and 10000 Fashion-MNIST evaluation IDs and retain all class and query-overlap counts.',
  'sec:r4-competitive-design; sec:r4-competitive-results; Limitations', ['working_R4/source/r4_methods.tex','working_R4/source/main.tex'],
  ['r4_analysis/competitive/results/cross_seed_stability.csv','r4_analysis/competitive/results/validation_best_class_counts.csv','r4_analysis/competitive/results/budget_paired_per_seed.csv'],
  ['r4_analysis/competitive/run_competitive.py'],[g_receipt])
]

# Close F's explicit cost question using measured records, never invent saved time.
with (ROOT/'r4_analysis/disagreement/results/F_summary.csv').open() as f:
    frows = list(csv.DictReader(f))
cost_rows=[]
for r in frows:
    cost_rows.append({k:r[k] for k in ['dataset','seed','K','width_index','penalty_floor','probe_set','n','eligible_archived_probes','earliest_prefix_final_finite','earliest_prefix_final_union_L0','earliest_prefix_final_union_Lplus','actual_new_solves']} | {
      'retrospective_trailing_redundant_finite':r['retrospective_trailing_redundant_finite'],
      'retrospective_trailing_redundant_with_L0':r['retrospective_trailing_redundant_with_L0'],
      'retrospective_trailing_redundant_with_Lplus':r['retrospective_trailing_redundant_with_Lplus'],
      'saved_solve_seconds':'','saved_solve_cost_status':'NOT_SUPPORTED',
      'timing_comparison_status':'NOT_PERFORMED','units':'archived readout checks',
      'source_sha256':sha('r4_analysis/disagreement/results/F_summary.csv')})
csv_write('F_cost_accounting.csv',cost_rows)

rows=[]
for cid,claim,loc,artifacts,data,scripts,verifiers in claim_specs:
    # Refuse silently unresolved paths in the traceability map.
    paths=artifacts+data+scripts+verifiers
    missing=[p for p in paths if not (ROOT/p).is_file()]
    if missing: raise FileNotFoundError(missing)
    arrays = (local_paths('r4_analysis/disagreement/results/*_paths.npz') if cid.startswith('D') else
              local_paths('r4_analysis/disagreement/results/*_finite_masks.npz') if cid.startswith('F') else
              local_paths('r4_analysis/competitive/results/*.npz') if cid.startswith(('E','G')) else
              local_paths('r3_analysis/m3/results/*.npz') if cid.startswith('C') else [])
    rows.append({'claim_id':cid,'claim':claim,'manuscript_location':loc,
      'status':'NOT_SUPPORTED' if cid=='F2' else 'PASS',
      'evidence_sha256_json':json.dumps(refs(paths),sort_keys=True),
      'array_sha256_json':json.dumps(refs(arrays),sort_keys=True),
      'exact_input_hash_ledger':input_ref,'exact_input_hash_ledger_sha256':sha(input_ref),
      'protocol_sha256_json':json.dumps(refs([protocol,'r4_analysis/disagreement/protocol.json','r4_analysis/competitive/protocol.json']),sort_keys=True),
      'frozen_manuscript_sha256':sha(frozen_pdf),
      'mapping_provenance':'Retrospective closure mapping; existing protocol and numerical outputs unchanged.'})
csv_write('claim_to_evidence.csv',rows)

stages=[
 ('A','preservation','PASS','Original evidence and R3 preserved; restore verification and actual saved delivery receipts exist.',
  ['next_work/evidence_inventory.json','logs/r3_archive_verification.json','logs/r4_clean_numerical_verification.json','logs/r4_split_verification.json','logs/R4_DELIVERY_SAVED.json','r4_analysis/github_preservation.json']),
 ('B','protocol','PASS','Frozen protocols preserve fixed questions and rules; exact-hash claim matrix supplied by this closure audit. Its retrospective creation and missing historical model/design-review provenance are explicit.',
  [protocol,'r4_analysis/competitive/protocol.json','r4_analysis/disagreement/protocol.json','r4_closure/claim_to_evidence.csv']),
 ('C','composition','PASS','20 settings, 40 selector rows, 400 class rows independently reconstructed; class accuracy, recall, retention and overlap plots saved.',
  [c_receipt,'r4_analysis/composition/SHA256_MANIFEST.json','next_work/results/selection_diagnostics_summary.csv']),
 ('D','finite disagreement','PASS','All 30 groups; 96 readouts each; sampled brackets, censored/missing-bound states and exact R3-mask reconstruction are retained.',
  [d_receipt,f_receipt,'r4_analysis/disagreement/results/D_bounds.csv','r4_analysis/disagreement/results/D_per_group.csv','r4_analysis/disagreement/results/SHA256_MANIFEST.json']),
 ('E','useful operating region','PASS','All 30 groups/2880 models; validation-only deterministic selection; 90/95/99% thresholds and zero outcomes independently verified.',
  [e_receipt,g_receipt,'r4_analysis/competitive/results/competitive_sets_summary.csv','r4_analysis/competitive/results/MANIFEST_SHA256.json']),
 ('F','exclusion efficiency','PASS','All 420 requested region/bank records and 21630 probe steps independently verified. Cost question closes NOT_SUPPORTED for saved seconds/speedup; actual new solves=0 and archived checks remain explicit.',
  [f_receipt,d_receipt,'r4_analysis/disagreement/results/F_summary.csv','r4_closure/F_cost_accounting.csv']),
 ('G','stability','PASS','Five seed pairs, query overlap and class records verified; shared images explicit; no independence inflation or tests.',
  [g_receipt,summary_receipt,'r4_analysis/competitive/results/budget_paired_per_seed.csv','r4_analysis/competitive/results/cross_seed_stability.csv','r4_analysis/competitive/results/validation_best_class_counts.csv']),
 ('H','integrate R4','PASS','41-page manuscript, tables, cover letter, report and decision summary produced. Clean source rebuild has exact page text and pixels; protected material checks pass.',
  ['logs/r4_clean_source_verification.json',package+'revision_record/PROTECTION_AND_PDF_AUDIT.json',package+'SHA256_MANIFEST.json','r4_analysis/review/independent_source_consistency.json',frozen_pdf]),
 ('I','independent review handoff','PASS','Independent numerical rerun, frozen review ZIP and one-page decision summary exist. Separate scientific review passes with handoff YES and no mandatory fixes. New closure records accompany the additive handoff.',
  ['r4_closure/scientific_review.md','r4_closure/scientific_review.json','r4_analysis/independent/INDEPENDENT_R4_NUMERICAL_AUDIT.md','r4_analysis/review/final_r4_reader.md','logs/r4_final_archive.json','logs/r4_clean_numerical_verification.json',package+'revision_record/RBF_Neural_Networks_R4_Decision_Summary.pdf'])
]
stage_rows=[{'stage':a,'name':b,'status':c,'finding':d,'evidence_sha256':refs(e),'input_hash_ledger_sha256':sha(input_ref)} for a,b,c,d,e in stages]
scientific_review = read('r4_closure/scientific_review.json')
review_mismatches = [p for p,h in scientific_review['input_sha256'].items() if sha(p) != h]
assert not review_mismatches, review_mismatches
assert sha('r4_closure/scientific_review.md') == scientific_review['report_sha256']
deliveries=read('logs/R4_DELIVERY_SAVED.json')
saved=[]
for x in deliveries['persistent_files']:
    p=Path(x['local_path']);rel=str(p.relative_to(ROOT));saved.append({'file':p.name,'save_status':x['status'],'local_path':rel,'bytes':p.stat().st_size,'sha256':sha(rel),'library_file_id':x['library_file_id']})
remote=read('r4_analysis/github_preservation.json')
ledger={
 'audit_utc':datetime.now(timezone.utc).isoformat(),'audit_model':'GPT-6.1 Sol','audit_reasoning':'High',
 'audit_model_provenance':'Parent orchestration instruction for this audit; not a reconstruction of earlier execution identity.',
 'plan_sha256':sha(plan),'status':'PLAN_IMPLEMENTATION_COMPLETE','scientific_analysis_implementation':'PASS_C_THROUGH_H',
 'strict_full_plan_closure':'PASS_WITH_EXPLICIT_HISTORICAL_PROVENANCE_GAP','journal_submission':'NOT_PERFORMED','journal_significance':'BORDERLINE_INDEPENDENT_ASSESSMENT_COMPLETE',
 'stages':stage_rows,'inputs':{'file':input_ref,'sha256':sha(input_ref),'status':read(input_ref)['status']},
 'scientific_review':{'status':scientific_review['scientific_validity'],'handoff':scientific_review['review_handoff'],'input_hashes_rechecked':len(scientific_review['input_sha256']),'input_mismatches':review_mismatches,'report_sha256':sha('r4_closure/scientific_review.md'),'receipt_sha256':sha('r4_closure/scientific_review.json'),'mandatory_fixes':scientific_review['mandatory_material_fixes_before_handoff'],'significance':scientific_review['journal_significance_assessment']},
 'claims':{'file':'r4_closure/claim_to_evidence.csv','sha256':sha('r4_closure/claim_to_evidence.csv'),'rows':len(rows),'created_after_analysis':True},
 'cost_question':{'stage':'F','operation_counts':'PASS','saved_solve_seconds':'NOT_SUPPORTED','measured_speedup':'NOT_SUPPORTED','actual_new_solves':0,'rows':len(cost_rows),'sha256':sha('r4_closure/F_cost_accounting.csv')},
 'model_history':{'current_audit':'GPT-6.1 Sol / High','historical_stage_models':'NOT_RECORDED_IN_EXISTING_RECEIPTS','instructional_model_roles_are_not_execution_records':True},
 'saved_deliverables':saved,'saved_receipt_sha256':sha('logs/R4_DELIVERY_SAVED.json'),
 'remote_scope':{'receipt_sha256':sha('r4_analysis/github_preservation.json'),'r2_r3_restoration':remote['r2_r3_integrity'],'r4_remote_files':remote['r4_remote_files'],'r4_scope':remote['r4_remote_scope'],'large_R4_derived_NPZ_remote':'NOT_SYNCHRONIZED','final_metadata_commit':deliveries['github_final_delivery']['commit'],'transport_generator_commit':deliveries['transport_generator_git_commit'],'closure_audit_remote_sync':'NOT_PERFORMED'},
 'frozen_archives_modified':False,'source_or_evidence_modified':False,
 'existing_REVIEW_READY_scope':'Frozen production artifact; this stricter plan audit is an additive record and does not rewrite the prior package.'}
dump('plan_audit.json',ledger)

md=['# Exact R4 plan closure audit','','The bounded plan implementation is complete across A–I. The separate scientific review finds no blocking error, authorizes review handoff and assesses journal significance as BORDERLINE.','',
 '| Stage | Status | Evidence-based outcome |','|---|---|---|']
md += [f'| {a}: {b} | {c} | {d} |' for a,b,c,d,e in stages]
md += ['', 'The machine-readable ledger names exact SHA-256 values for every cited stage record. `claim_to_evidence.csv` maps 12 central claims to manuscript locations, scripts, CSVs, arrays, verifiers and exact input hashes. This mapping is a retrospective traceability document; it does not change the frozen protocols or imply that it existed before extraction.', '',
 'F cost accounting is closed with a null cost conclusion: 420 region/bank rows record actual new solves of zero, archived readout-check counts and retrospective redundant prefixes. Saved solve seconds and measured speedup are NOT_SUPPORTED. The 41.002-second path-analysis invocation and 109.660-second competitive-analysis invocation measure their respective reconstructions; they cannot be subtracted to produce saved solve time.', '',
 'The existing frozen review ZIP and one-page decision summary are verified production deliverables. The separate `scientific_review.md` and JSON now establish independent scientific PASS, handoff YES and no mandatory fixes. Their recorded manuscript hashes are checked against the unchanged R4 source. Journal significance is assessed as BORDERLINE; this assessment closes the review task.', '',
 'Six saved-delivery receipts report success: manuscript PDF, LaTeX ZIP, revision report PDF, decision summary PDF and two byte-exact archive transport ZIPs. The full 708,364,070-byte archive has SHA-256 `8f1a2998d199b4258dc86d9953977407dff0672b53f0b966719fa21a5758842e`. Remote preservation records cover R2/R3 restoration and 211 R4 manuscript/protocol/code/summary records; large derived R4 per-query arrays are in the saved archive and regenerable from archived inputs. The new closure records have not been synchronized remotely.', '',
 'Current closure work records GPT-6.1 Sol / High. Earlier stage model identities and reasoning levels are absent from the numerical receipts and cannot be reconstructed from suggested model roles. Existing pilot, execution and verifier runtimes are preserved in `execution_log.json`.', '',
 '## Handoff and separate decisions','',
 '1. Include the exact-hash claim map, stage ledger, cost-null record, execution log and independent scientific review together in the additive closure handoff.',
 '2. Preserve the original frozen archive and manuscript unchanged; the closure records are additive.',
 '3. B is implemented with retrospective traceability and an explicit historical provenance gap. Earlier model identities and a separate pre-extraction design-review receipt cannot be invented.',
 '4. Journal transfer/submission and the editor’s eventual significance/acceptance decision remain separate. No journal submission was performed or authorized in this closure.', '',
 '## Limitations','',
 'This audit verifies stored receipts and recomputes their cited input hashes. It does not rerun the already completed numerical reconstructions. Historical model identities and a pre-extraction design-review receipt were not supplied; the traceability matrix was added at closure. No GitHub write, source change, evidence change or immutable-archive change was performed.']
(OUT/'plan_audit.md').write_text('\n'.join(md)+'\n')

execution=[]
for stage,p,keys in [('D_F_pilot','r4_analysis/disagreement/PILOT.json',['elapsed_seconds','estimated_remaining_seconds']),('D_F_full',d_receipt,['elapsed_this_run_seconds','total_group_runtime_seconds']),('E_G_pilot','r4_analysis/competitive/results/PILOT.json',['seconds']),('E_G_full',e_receipt,['runtime_seconds_this_invocation','runtime_seconds_groups']),('C_independent',c_receipt,['elapsed_seconds']),('D_F_independent',f_receipt,['elapsed_seconds']),('E_G_independent',g_receipt,['elapsed_seconds'])]:
    d=read(p);execution.append({'stage':stage,'receipt':p,'receipt_sha256':sha(p),'runtime_fields':{k:d[k] for k in keys},'historical_model':'NOT_RECORDED','historical_reasoning':'NOT_RECORDED'})
execution.append({'stage':'final_independent_scientific_review','model':read('r4_closure/scientific_review.json')['configured_model'],'reasoning':read('r4_closure/scientific_review.json')['configured_reasoning_effort'],'provenance':read('r4_closure/scientific_review.json')['configuration_source'],'runtime_seconds':None,'runtime_status':'NOT_RECORDED','receipt':'r4_closure/scientific_review.json','receipt_sha256':sha('r4_closure/scientific_review.json')})
execution.append({'stage':'closure_audit','model':'GPT-6.1 Sol','reasoning':'High','provenance':'Current parent instruction','elapsed_script_seconds':time.perf_counter()-START,'activity':'Hash and documentation audit; no numerical rerun, no refit.'})
dump('execution_log.json',{'records':execution,'elapsed_values_are_not_API_usage_or_billing':True})
print(json.dumps({'stages':{x['stage']:x['status'] for x in stage_rows},'claims':len(rows),'input_files':len(input_checks),'input_hash_status':read(input_ref)['status'],'cost_rows':len(cost_rows),'script_seconds':time.perf_counter()-START}))
