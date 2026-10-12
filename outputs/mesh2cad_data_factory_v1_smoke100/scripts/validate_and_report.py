"""Read completed cases, verify artifact chain and write a new report snapshot."""
import sys, json, csv, platform, socket, subprocess
from pathlib import Path
from collections import Counter
import numpy as np
import cadquery, OCP, trimesh, scipy, shapely
from factory import ROOT, CONFIG, SEED, TAXONOMY, sha, write, guard, now, evaluate, load
from execute_program import validate

def csvwrite(path,rows,fields=None):
    fields=fields or list(rows[0]) if rows else fields or ['case_id']
    with path.open('x',newline='') as f:
        w=csv.DictWriter(f,fieldnames=fields,extrasaction='ignore');w.writeheader();w.writerows(rows)

def checks():
    failures=[]; rejected=[]
    bad=['import trimesh\nresult = trimesh.load("x.stl")',
         'import cadquery as cq\nresult = cq.importers.importStep("x.step")',
         'import cadquery as cq\nvertices = [[0,0,0]]\nresult = cq.Workplane("XY")',
         'import cadquery as cq\nresult = cq.Workplane("XY").box(1,1,1)\nopen("bad")',
         'import cadquery as cq\nfor i in [1]:\n result = cq.Workplane("XY").box(1,1,1)']
    for s in bad:
        try: validate(s); failures.append('unsafe code admitted')
        except (SyntaxError,ValueError): rejected.append(True)
    validate('import cadquery as cq\nresult = cq.Workplane("XY").box(1,1,1)\n')
    box=trimesh.creation.box(); same=evaluate(box,box,SEED)
    shifted=box.copy();shifted.apply_translation([.25,0,0]); offset=evaluate(box,shifted,SEED)
    if same['iou']!=1 or not same['strict_pass'] or offset['strict_pass'] or abs(offset['bbox_center_error']-.25)>1e-8:
        failures.append('geometry invariant failure')
    return {'pass':not failures,'errors':failures,'unsafe_programs_rejected':len(rejected),'identity_box':same,'translated_box':offset,
            'note':'Safety allowlist is a generator contract, not a general adversarial Python sandbox; no untrusted arbitrary code is ingested.'}

def main():
    tag=sys.argv[1]; output=ROOT/'reports'/tag;output.mkdir(exist_ok=False)
    rows=[json.loads(p.read_text()) for p in sorted((ROOT/'cases').glob('*/manifest.json'))]
    errors=[]; table=[]
    for r in rows:
        exs=[a['execution'] for a in r['attempts']]; m=r['geometry_metrics'];d=ROOT/'cases'/r['case_id']
        for key in ['source_mesh_sha256','source_object_id','source_part_id','parent_object_id','split_group_id']:
            if not r.get(key): errors.append(r['case_id']+': missing '+key)
        if r['source_valid']:
            f=np.asarray(r['normalization']['forward_transform']);inv=np.asarray(r['normalization']['inverse_transform'])
            if not np.allclose(f@inv,np.eye(4),atol=1e-10):errors.append(r['case_id']+': inverse transform')
        if m:
            validate(Path(r['cad_program_path']).read_text())
            if sha(r['step_path'])!=m['step_sha256'] or sha(r['cad_mesh_path'])!=m['cad_mesh_sha256'] or sha(d/'normalized/normalized_mesh.ply')!=m['source_mesh_sha256']:
                errors.append(r['case_id']+': evaluation chain hash mismatch')
            if not r['execution']['step_reload_pass']:errors.append(r['case_id']+': reload missing')
            strict=(m['iou']>=.90 and m['normalized_chamfer']<=.01 and m['bbox_error']<=.03 and m['centroid_l2_error']<=.02)
            if (r['filter_decision']=='STRICT_ACCEPT')!=strict:errors.append(r['case_id']+': filter inconsistency')
        if r['failure_reason'] and r['failure_reason'] not in TAXONOMY:errors.append(r['case_id']+': unknown taxonomy value')
        t={k:r.get(k) for k in ['case_id','source_dataset','source_object_id','source_part_id','split_group_id','source_mesh_path','source_mesh_sha256','source_valid','direct_attempted','filter_decision','failure_reason','cad_program_path','step_path','cad_mesh_path']}
        for flag in ['parse_pass','execute_pass','step_export_pass','step_reload_pass']:t[flag]=any(e.get(flag,False) for e in exs)
        t.update({k:m.get(k) for k in ['normalized_chamfer','iou','bbox_error','centroid_l2_error']})
        t.update(attempt_n=len(exs),watertight=r.get('source_audit',{}).get('watertight'),provenance_closed=r.get('provenance_closed',False))
        table.append(t)
    selftests=checks();write(output/'selftests.json',selftests)
    g=guard();write(output/'read_only_guard.json',g)
    overall={'requested':100,'located':len(json.loads((ROOT/'manifests/selection_frozen.json').read_text())['cases']),
             'completed':len(rows),'source_valid':sum(r['source_valid'] for r in rows),'direct_attempted':sum(r['direct_attempted'] for r in rows)}
    for key in ['parse_pass','execute_pass','step_export_pass','step_reload_pass']:overall['cad_'+key if key in ['parse_pass','execute_pass'] else key]=sum(t[key] for t in table)
    for key,decision in [('strict_accept','STRICT_ACCEPT'),('relaxed_only','RELAXED_ANALYSIS_ONLY'),('reject','REJECT')]:overall[key]=sum(r['filter_decision']==decision for r in rows)
    counts=Counter(r['failure_reason'] for r in rows if r['failure_reason'])
    failures=[dict(failure_reason=k,count=counts[k],percentage=100*counts[k]/max(1,len(rows))) for k in TAXONOMY]
    distributions=[]
    for k in ['normalized_chamfer','iou','bbox_error','centroid_l2_error']:
        a=np.array([r['geometry_metrics'][k] for r in rows if r['geometry_metrics']])
        distributions.append(dict(metric=k,N=len(a),**({ 'mean':float(a.mean()),'median':float(np.median(a)),
           'p25':float(np.percentile(a,25)),'p75':float(np.percentile(a,75)),'p90':float(np.percentile(a,90)),
           'min':float(a.min()),'max':float(a.max())} if len(a) else {})))
    write(output/'overall.json',overall);write(output/'metric_distributions.json',distributions)
    csvwrite(output/'smoke100_case_table.csv',table)
    for name,decision in [('accepted_cases','STRICT_ACCEPT'),('relaxed_cases','RELAXED_ANALYSIS_ONLY'),('rejected_cases','REJECT')]:
        csvwrite(output/(name+'.csv'),[t for t in table if t['filter_decision']==decision],list(table[0]))
    csvwrite(output/'failure_breakdown.csv',failures)
    csvwrite(output/'metric_distributions.csv',distributions)
    csvwrite(output/'overall.csv',[overall])
    csvwrite(output/'direct_vs_fallback.csv',[{'branch':'DIRECT','attempted':overall['direct_attempted'],'execution_success':overall['cad_execute_pass'],
        'step_reload':overall['step_reload_pass'],'strict_accept':overall['strict_accept'],'comparison':'not a matched fallback comparison'},
        {'branch':'P3_XPART','attempted':0,'execution_success':0,'step_reload':0,'strict_accept':0,'comparison':'not attempted; benefit unknown'}])
    versions={'python':sys.version,'cadquery':cadquery.__version__,'OCP':OCP.__version__,'trimesh':trimesh.__version__,
       'numpy':np.__version__,'scipy':scipy.__version__,'shapely':shapely.__version__,'hostname':socket.gethostname(),
       'runtime_timestamp':now(),'random_seed':SEED,'git_commit':None,'git_note':'Factory is a new output directory; source reuse tracked by file SHA256.'}
    write(output/'software_versions.json',versions)
    stage_hashes=[json.loads(p.read_text()) for p in sorted((ROOT/'stages').glob('*/code_config_hashes.json'))]
    core=['scripts/factory.py','scripts/execute_program.py','scripts/fit_logic.py','config/factory_config.json','config/thresholds.json']
    frozen=bool(stage_hashes) and all(all(h.get(k)==stage_hashes[0].get(k)==sha(ROOT/k) for k in core) for h in stage_hashes)
    stages=[json.loads(p.read_text()) for p in sorted((ROOT/'stages').glob('*/validation.json'))]
    stable=not errors and selftests['pass'] and frozen and g['status']=='PASS' and all(s['pass'] for s in stages) and len(rows)==100 and len(stages)==3
    if any(r['failure_reason'] in ['UNKNOWN','EVALUATOR_FAILURE','SOURCE_PROVENANCE_FAILURE'] for r in rows):stable=False
    status={'current_gate':'SMOKE100_PASS' if stable else 'SMOKE100_BLOCKED','read_only_guard':g['status'],
        'can_scale_to_1000':stable,'next_allowed_stage':'SCALE_1000' if stable else 'FIX_DATA_FACTORY',
        'primary_blocker':None if stable else {'artifact_errors':errors,'frozen':frozen,'stage_results':stages},
        'native_cadquery_enforced':True,'mesh_wrapper_rejected':selftests['unsafe_programs_rejected']==5,
        'provenance_closed':all(r.get('provenance_closed',False) for r in rows if r['source_valid']),
        'coordinate_protocol_frozen':frozen,'unified_evaluator_frozen':frozen,'object_split_id_available':True,
        'surface_cache_status':'NOT_BUILT','curve_cache_status':'NOT_BUILT','fallback_needed_n':0,'fallback_attempted_n':0,
        'fallback_step_reload_n':0,'fallback_strict_accept_n':0,'fallback_needed_interpretation':'0 independently confirmed; actual completion necessity is not established by nonwatertightness.',
        'p3_xpart_role':'OPTIONAL_FALLBACK_BRANCH_NOT_USED','overall':overall,'metric_distributions':distributions,'failures':counts}
    write(output/'status.json',status)
    md=f'''# MESH2CAD DATA FACTORY V1 — Smoke100

CURRENT_GATE = {status['current_gate']}
READ_ONLY_GUARD = {g['status']}

These are geometry-consistent reconstructed CAD targets / pseudo-CAD supervision, not original design ground truth.

## Answers to the 11 required questions

1. Located {overall['located']} frozen source candidates; {overall['source_valid']} source-valid, provenance-closed meshes processed. Closure is anchored to extant original part STL bytes, historical source SHA metadata, parent whole-object STL bytes, and exact float32 triangle subset membership. Original GLB/labels/download chain remain unavailable; no broader upstream closure is claimed.
2. Direct reconstruction attempted: {overall['direct_attempted']}.
3. Direct case-level successes (any candidate): parse {overall['cad_parse_pass']}; execution {overall['cad_execute_pass']}; STEP export {overall['step_export_pass']}; STEP reload {overall['step_reload_pass']}; strict geometry pass {overall['strict_accept']}.
4. Final strict accepted direct pair count: {overall['strict_accept']}. Relaxed analysis only: {overall['relaxed_only']}; rejected: {overall['reject']}.
5. Final case failures: {dict(counts)}. Individual candidate errors remain in each case manifest and attempts directory. A failed hypothesis does not invalidate a later successful candidate.
6. Independently confirmed P3/X-Part-needed cases: 0. This is an evidence-qualified count, not proof no mesh would benefit. Open part boundaries or template mismatch alone do not justify completion.
7. Completion attempted 0; fallback CAD reconstructed 0; fallback strict accepted 0.
8. Completion benefit is UNKNOWN / not tested. The observed fit failures concern the bounded CAD hypotheses; no causal evidence attributes them to missing source surfaces.
9. Native executable CadQuery cases: {overall['cad_execute_pass']}. DSL targets = 0; mesh-wrapper targets = 0. Rejected/no-plan cases have no accepted target. AST allowlist rejects mesh import/payloads; genuine 2D polygon sketches are capped at 96 entities, 4 profiles, 8 holes.
10. Can scale to 1000: {'YES' if stable else 'NO'}. No Scale1000 execution was performed.
11. Primary blocker: {status['primary_blocker']}. Next allowed stage: {status['next_allowed_stage']}.

## Source selection and limitations

The metadata-eligible pool contained 2105 original part meshes. Selection prioritizes historical watertight status, low face count, then a deterministic object/part hash; exact-byte duplicates are removed. No historical CAD metric was used. The frozen 100 are strongly biased toward simple geometry, not a representative benchmark or category-balanced dataset. Source audit reports connected components, boundary/nonmanifold edges, finite vertices, valid faces, area and meaningful volume. Nonwatertight meshes are not automatically rejected or completed.

Every case carries dataset, object/part IDs, source/evidence/parent hashes and `split_group_id`. Future splits must group all parts of one parent object. Source hashes deduplicate identical STL bytes, not semantic duplicates across different objects.

## Coordinate and metric contract

Canonical vertices = (original vertices − original bbox midpoint) / original longest bbox edge. Source orientation is preserved. Forward and inverse 4x4 matrices, original/canonical bboxes and area-weighted centroids are retained. Local modeling axes do not rotate the evaluation frame. CAD is never independently aligned.

Each candidate is executed in a fresh subprocess, exported, reloaded with CadQuery/OCC, validated for nonempty valid solid B-Rep, then tessellated at tolerance 0.001 and angular tolerance 0.05. Only serialized tessellation of the reloaded STEP is evaluated. STEP, CAD mesh and normalized source hashes bind metrics to artifacts.

Chamfer uses 20000 area-uniform surface points per mesh, deterministic seeds, symmetric mean of unsquared nearest sampled-point distances. NCD divides this mean by the source bbox diagonal. P95 pools both directional distances. This sampled-point metric has sampling noise even on identical surfaces. Centroid is the exact triangle-area-weighted surface centroid; errors are canonical length units. Bbox error is max(center L2, extent L-infinity).

IoU protocol: APPROXIMATE_VOXEL_SCAN_FILL_IOU_V1, nominal resolution 128. One shared union-bbox grid, longest union extent /124 pitch, padded boundary cells; subdivision surface rasterization, majority XYZ scan fill and binary hole fill. This is approximate scan-filled occupancy, NOT exact solid volumetric IoU. Open sheets can receive occupancy without defining a physical enclosed volume. It is unsuitable to interpret these scores as original design validity.

Strict: approximate IoU >=0.90, NCD <=0.01, bbox error <=0.03, centroid error <=0.02 plus source/native/execution/export/reload/evaluation gates. Relaxed: all execution and evaluation gates valid but strict metrics fail. Reject: invalid source, program, execution, export/reload or evaluator. Thresholds are smoke references, not final training thresholds.

Four or fewer deterministic hypotheses per source: up to two projected silhouette extrusions, an oriented box and a cylinder. Selection ranks strict pass, then IoU, then NCD. This is finite template selection, no iterative loss optimization, LLM calls, model updates or training. Acceptance is measured on the same source used for fitting and candidate selection, not held-out reconstruction generalization.

## Reproducibility, guard and caches

Stage validation: {stages}. Core generator/config/evaluator SHA unchanged across stages: {frozen}. Safety/metric self-tests: {selftests['pass']}. Artifact consistency errors: {errors}.

Read-only guard verifies {g['hash_checked_n']} protected file hashes and {g['metadata_checked_n']} preexisting historical file metadata entries. Access times are excluded. Scope is selected source/parent/evidence, copied donor, frozen historical audit and relevant source/output trees; this is not a server-wide filesystem proof. All writes from factory code are under the fresh factory root, and historical logic is copied rather than imported. Existing case/stage/report directories are never overwritten; reruns require a new root or a new report tag. No historical rename, deletion, training or bulk generation occurred.

Surface/curve caches: NOT_BUILT. No compatible extractor was validated for this new contract; status and reason recorded per case. This optional omission does not gate Smoke100. Software versions, seeds, source hash inventory, code hashes and code reuse provenance are supplied.

## Deliverables and entrypoint

Factory root: `{ROOT}`

Entrypoint: `scripts/factory.py --limit 3`, then `--limit 10`, then `--limit 100` with the recorded cadfit-env Python. Each later stage requires the previous stage's validation pass and reruns the historical integrity guard. This frozen run is capped at 100; future scale requires a new root/config and source selection, never reusing this run as mutable storage.

Audit/report: `scripts/validate_and_report.py <new_snapshot_tag>`.

Tables: `tables/smoke100_case_table.csv`, `accepted_cases.csv`, `relaxed_cases.csv`, `rejected_cases.csv`, `failure_breakdown.csv`, `metric_distributions.csv`, `overall.csv`, `direct_vs_fallback.csv`.

Manifests: `manifests/cases.jsonl`, `source_inventory.csv`, `selection_frozen.json`. Each `cases/case_*/manifest.json` contains all candidate metadata, failures, paths, normalization, metrics, decisions and cache status. Full candidate programs, STEP files, reload metadata, tessellated meshes and logs remain inspectable.
'''
    (output/'FINAL_REPORT.md').write_text(md)
    if tag=='final':
        import shutil
        for p in output.glob('*.csv'):shutil.copyfile(p,ROOT/'tables'/p.name)
        with (ROOT/'manifests/cases.jsonl').open('x') as f:
            for r in rows:f.write(json.dumps(r,allow_nan=False)+'\n')
        inventory=[{k:r[k] for k in ['case_id','source_dataset','source_object_id','source_part_id','source_mesh_path','source_mesh_sha256','parent_mesh_path','parent_mesh_sha256','source_evidence_path','source_evidence_sha256','split_group_id']} for r in rows]
        csvwrite(ROOT/'manifests/source_inventory.csv',inventory)
        shutil.copyfile(output/'FINAL_REPORT.md',ROOT/'reports/FINAL_REPORT.md')
    print(json.dumps(status))

if __name__=='__main__':main()
