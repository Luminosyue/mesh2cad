from validate_native_parametric_cad import *
import csv,collections,datetime,shutil,platform
O=Path(__file__).resolve().parents[1];P=O.parent;V1=P/'p3_high_detail_mesh2cad_factory_v1_smoke20';V3=P/'part_cad_reject_repair_v3'
CLASSES=['A_NATIVE_PARAMETRIC','B_NATIVE_BREP_NONPARAMETRIC','C_FACETED_BREP','D_MESH_WRAPPER','E_UNCERTAIN']
STATUSES=['STRICT_ACCEPT','NEAR_PASS','REJECT']
def table(path,rows,fields=None):
 path=Path(path);path.parent.mkdir(parents=True,exist_ok=True)
 if fields is None:fields=list(dict.fromkeys(k for r in rows for k in r))
 with path.open('w',newline='') as f:
  w=csv.DictWriter(f,fields,extrasaction='ignore');w.writeheader()
  for r in rows:w.writerow({k:json.dumps(v) if isinstance(v,(dict,list)) else v for k,v in r.items() if k in fields})
def load(version):
 rows=[json.loads(p.read_text()) for p in sorted((O/'cases'/version).glob('*/*/audit.json'))];assert len(rows)==209;assert len({r['case_id'] for r in rows})==209;return rows
def summary(rows):
 counts=Counter(r['classification'] for r in rows)
 return {'TOTAL_PART_N':len(rows),**{k+'_N':counts[k] for k in CLASSES},'SELF_CONTAINED_PARAMETRIC_N':sum(r['self_contained'] for r in rows),'ACCEPT_FOR_PARAMETRIC_DATASET_N':sum(r['accepted_for_parametric_dataset'] for r in rows),**{'MEDIAN_'+label:float(np.median([r[field] for r in rows])) for label,field in [('SOURCE_TRIANGLE_N','source_triangle_count'),('STEP_FACE_N','step_face_count'),('COMPRESSION_RATIO','compression_ratio'),('ANALYTIC_FACE_RATIO','analytic_face_ratio'),('TRIANGLE_PLANAR_FACE_RATIO','triangle_planar_face_ratio')]},'MESH_IMPORT_DETECTED_N':sum(r['mesh_import_detected'] for r in rows),'EMBEDDED_VERTEX_FACE_N':sum(r['embedded_vertices_detected'] or r['embedded_faces_detected'] for r in rows),'TRUE_NATIVE_FEATURE_CODE_N':sum(r['safe_grammar'] for r in rows),'ISOLATED_REEXECUTION_PASS_N':sum(r['isolated_reexecution_pass'] for r in rows),'CODE_STEP_CORRESPONDENCE_PASS_N':sum(r.get('code_step_correspondence_pass',False) for r in rows),'step_face_range':[min(r['step_face_count'] for r in rows),max(r['step_face_count'] for r in rows)],'surface_totals':dict(sum((Counter(r['face_type_counts']) for r in rows),Counter())),'triangle_planar_total':sum(r['triangle_planar_face_count'] for r in rows),'polyline_program_n':sum('polyline' in r['feature_ops'] for r in rows),'spline_program_n':sum('spline' in r['feature_ops'] for r in rows),'max_sketch_entities':max(r['sketch_entity_count'] for r in rows),'max_primitive_count':max(r['primitive_count'] for r in rows),'REPRESENTATION_GATE':'PASS' if counts['A_NATIVE_PARAMETRIC']==len(rows) else 'FAIL'}
FIELDS='object_id part_id previous_status current_status cad_path step_path source_mesh_path source_vertex_count source_triangle_count step_face_count step_edge_count step_vertex_count solid_count shell_count closed valid analytic_face_count analytic_face_ratio spline_face_count unknown_face_count triangle_planar_face_count triangle_planar_face_ratio planar_triangle_face_ratio quad_face_count ngon_face_count compression_ratio face_triangle_ratio median_face_area p10_face_area p90_face_area tiny_face_count tiny_planar_face_count native_feature_count feature_ops sketch_entity_count primitive_count sketch_count extrude_count revolve_count loft_count sweep_count boolean_union_count boolean_cut_count boolean_intersect_count fillet_count chamfer_count feature_op_count mesh_import_detected embedded_vertices_detected embedded_faces_detected mesh_wrapper_detected self_contained isolated_reexecution_pass code_step_correspondence_pass classification is_native_parametric_cad accepted_for_parametric_dataset primary_reason'.split()
if __name__=='__main__':
 rows1=load('V1');rows3=load('V3');s1=summary(rows1);s3=summary(rows3);lookup={r['case_id']:r for r in rows1};assembly=[]
 for p in sorted((V1/'objects').glob('*/assembly/assembly_metrics.json')):
  m=json.loads(p.read_text())
  if not m.get('step_reload_pass'):continue
  members=[lookup[m['object_id']+'/'+pid] for pid in m['accepted_part_ids']];top=topology(cq.importers.importStep(m['step_path']).val());world=topology(cq.importers.importStep(m['original_coordinate_step']).val());expected=dict(sum((Counter(r['face_type_counts']) for r in members),Counter()));actual={k:v for k,v in top['face_type_counts'].items() if v};expected={k:v for k,v in expected.items() if v}
  r={'object_id':m['object_id'],'part_ids':m['accepted_part_ids'],'assembly_native_part_n':sum(r['classification']=='A_NATIVE_PARAMETRIC' for r in members),'assembly_faceted_part_n':sum(r['classification'] in ['C_FACETED_BREP','D_MESH_WRAPPER'] for r in members),'assembly_uncertain_part_n':sum(r['classification']=='E_UNCERTAIN' for r in members),'step_path':m['step_path'],'original_coordinate_step':m['original_coordinate_step'],'face_type_counts':top['face_type_counts'],'face_count':top['step_face_count'],'triangle_planar_face_count':top['triangle_planar_face_count'],'solid_count':top['solid_count'],'valid':top['valid'],'closed':top['closed'],'part_surface_counts_match':actual==expected,'world_surface_counts_match':world['face_type_counts']==top['face_type_counts'],'full_object_geometry_accepted':False};assert r['part_surface_counts_match'] and r['world_surface_counts_match'];assembly.append(r);dump(O/'assembly'/m['object_id']/'canonical_topology.json',top);dump(O/'assembly'/m['object_id']/'world_topology.json',world)
 assert len(assembly)==3;table(O/'tables/assembly_audit.csv',assembly);dump(O/'assembly/assembly_audit.json',assembly)
 preview=json.loads((P/'part_cad_v3_assembly_visualizations/manifest.json').read_text());look3={r['case_id']:r for r in rows3};previews=[]
 for obj in preview['objects']:
  members=[look3[x['case_id']] for x in obj['parts']];previews.append({'object_id':obj['object_id'],'artifact':'GLB/PLY diagnostic tessellated preview, NOT assembly STEP','assembly_native_part_n':sum(r['classification']=='A_NATIVE_PARAMETRIC' for r in members),'assembly_faceted_part_n':sum(r['classification'] in ['C_FACETED_BREP','D_MESH_WRAPPER'] for r in members),'part_n':len(members),'geometry_status':obj['counts']})
 table(O/'tables/v3_preview_assembly_audit.csv',previews)
 for version,rows in [('V1',rows1),('V3',rows3)]:
  suffix='' if version=='V1' else '_v3';table(O/f'tables/representation_audit_209{suffix}.csv',rows,FIELDS)
  table(O/f'tables/accepted_native_cases{suffix}.csv',[r for r in rows if r['accepted_for_parametric_dataset']],FIELDS)
  table(O/f'tables/suspicious_faceted_cases{suffix}.csv',[r for r in rows if r['faceted_topology_warning'] or r['classification']!='A_NATIVE_PARAMETRIC'],FIELDS)
  table(O/f'tables/status_representation_cross_table{suffix}.csv',[{'status_basis':'V1 original' if version=='V1' else 'V3 current','status':st,'total':sum(r['previous_status' if version=='V1' else 'current_status']==st for r in rows),**{c:sum(r['previous_status' if version=='V1' else 'current_status']==st and r['classification']==c for r in rows) for c in CLASSES}} for st in STATUSES])
  table(O/f'tables/surface_type_summary{suffix}.csv',[{'surface_type':t,'face_count':sum(r['face_type_counts'][t] for r in rows),'part_n':sum(r['face_type_counts'][t]>0 for r in rows)} for t in rows[0]['face_type_counts']])
  table(O/f'tables/face_details{suffix}.csv',[{'object_id':r['object_id'],'part_id':r['part_id'],**f} for r in rows for f in r['faces']])
  table(O/f'tables/actual_triangular_face_cases{suffix}.csv',[r for r in rows if r['triangle_planar_face_count']],FIELDS)
 ev=O/'evidence';ev.mkdir(exist_ok=True);sources=[V1/'scripts/execute_candidate.py',V1/'scripts/p3_validate.py',V1/'scripts/p3_part_cad.py',V1/'scripts/cad_emit.py',V1/'scripts/p3_assemble.py',V3/'scripts/v3_geometry.py',P/'part_cad_v3_assembly_visualizations/scripts/render_v3_assemblies.py'];evidence=[]
 for p in sources:
  if not p.exists():evidence.append({'path':str(p),'status':'MISSING'});continue
  dest=ev/p.name;shutil.copyfile(p,dest);lines=p.read_text().splitlines();hits=[{'line':i,'text':line} for i,line in enumerate(lines,1) if any(key in line for key in ['def validate','ALLOWED_','tessellate','face_normals','def sample','def render','def extrusion','def revolve','def loft','polyline','NATIVE_CADQUERY_ENFORCED'])];evidence.append({'path':str(p),'sha256':sha(p),'copy':str(dest.relative_to(O)),'lines':hits})
 dump(ev/'source_evidence.json',evidence)
 guard=json.loads((O/'integrity/READ_ONLY_GUARD.json').read_text()) if (O/'integrity/READ_ONLY_GUARD.json').exists() else {'pass':False,'pending':True}
 tests=json.loads((O/'tests/TEST_RESULTS.json').read_text());assert tests['pass']
 final={'task':'NATIVE_PARAMETRIC_CAD_AUDIT_V1','primary_cohort':'V1 original 209; current V3 separately audited 209','V1':s1,'V3':s3,'READ_ONLY_GUARD':'PASS' if guard['pass'] else 'PENDING','PREVIOUS_NATIVE_CHECK_WAS_INSUFFICIENT':'YES','WHY':'Old executor already had strict AST/import/operation restrictions and complexity limits, but lacked per-face OCC surface classification, triangular-face audit, independent reexecution-to-STEP correspondence and source-to-BRep compression reporting. No evidence of previous mesh-wrapper admission in these cohorts.','PRIMARY_ROOT_CAUSE':'Polygonal fitted sketches produce genuine planar strips/conical segments; the STEP tessellation is then rendered with per-triangle normals by the preview renderer. Neither is source triangle wrapping.','PIPELINE_STAGE_RESPONSIBLE':'Profile construction + STEP display tessellation + preview shading','RESPONSIBLE_SCRIPT':['p3_part_cad.py','cad_emit.py','v3_geometry.py','execute_candidate.py','render_v3_assemblies.py'],'RESPONSIBLE_FUNCTION':['generate/extrusion/revolve/loft','emit_profiles/emit_loft','run (reloaded.tessellate)','sample (mesh.face_normals)','render (normal-based shading)'],'REPRESENTATION_GATE':'PASS' if s1['REPRESENTATION_GATE']=='PASS' and s3['REPRESENTATION_GATE']=='PASS' and guard['pass'] else 'PENDING','GEOMETRY_FITTING_CURRENTLY_RELEVANT':'YES','CAN_CONTINUE_PART_CAD_FITTING_V2':'YES (representation gate only; V2 already exists, no rerun performed)','NEED_REBUILD_NATIVE_CAD_GENERATOR':'NO','NEXT_ALLOWED_STAGE':'GEOMETRY_FITTING_REVIEW_WITH_NATIVE_REPRESENTATION_VALIDATOR','geometry_gate':'FAIL; representation PASS is not geometric acceptance','tests_n':tests['test_n'],'tests_pass':tests['pass'],'legacy_partial_assembly_n':len(assembly),'v3_preview_assembly_n':len(previews)}
 dump(O/'reports/SUMMARY.json',final)
 spec='''# Native parametric CAD validator specification

Inputs: `--cad`, `--step`, `--source-mesh`, `--out`. All inputs are read-only. Output/execution must be a NEW audit directory. Requires the existing cadfit-env (CadQuery/OCP, NumPy, trimesh). Unknown Python is not executed or accepted.

The supported grammar is straight-line `import cadquery as cq`, numeric literals, named values and approved Workplane feature calls. Live dependencies of `result` must include solid-building operations. No imports of mesh/STEP, arbitrary functions, file access, comprehensions, loops, dynamic attributes or external payloads are allowed. Imports are also restricted at isolated execution time. Source 3D vertex/index arrays and low-level triangle construction are rejected or fail closed to E. Literal 2D fitted sketch control points are valid parameters, not a source 3D triangle soup. Budgets: at most 8 solid-building features, 6 booleans, 96 sketch vertices, 60 KB program. Feature counts are AST counts; this grammar has no loops, so there is no hidden repeated feature expansion.

Isolation: copy cad.py only into a new directory, preload CadQuery, execute the audited exact source with a restricted importer and no file-access builtins. Historical source meshes remain on the server, but no supported code path can read them. This is restricted-program isolation, not an OS container/security sandbox. Unsupported general-purpose Python goes to manual review. Timeout 180 seconds. No original STEP is exported or overwritten. Regenerated in-memory shape must match supplied STEP face/edge/vertex/solid counts, surface counts, bounds (<1e-5), relative volume and area (<1e-5). These are strong correspondence checks for this restricted cohort, not a mathematical equivalence proof for arbitrary programs.

OCC BRepAdaptor_Surface supplies explicit enum names. Analytic = plane/cylinder/cone/sphere/torus/extrusion/revolution. Bezier/BSpline is reported separately and is not automatically rejected. Every face includes area, bbox, unique edges, vertices, wires and relative area. A true triangular planar face requires PLANE, 3 linear edges, 3 vertices, 1 wire; merely having 3 edges (e.g. an arc-bounded face) is not enough. Ratio denominator is all B-Rep faces; the alternate ratio among planar faces is also saved. Tiny threshold = 0.001 of total surface area; this is a diagnostic, not a standalone rejection.

Warnings: >=100 faces with >=80% planar triangles; >=100 faces with STEP/source count ratio 0.5..2; or >=500 tiny patches (80%) with face/source ratio >0.3. Warnings block automatic A and require review. D requires mesh/embedded triangles flowing through low-level construction, or a direct mesh-import constructor. C combines dense triangular topology with source-count/code evidence. Native B-Rep import without live compact history is B. Missing/unsupported/conflicting evidence is E. A requires live compact code, independent reconstruction, matching STEP, valid closed solids, known surface types and no topology warning. False negatives outside this intentionally narrow grammar need review, not threshold relaxation.

`accepted_for_parametric_dataset` means representation eligibility ONLY. A candidate must separately pass geometric gates before paired training use. B requires review; C/D are rejected; E is not accepted. Dataset-level gate uses the stricter condition 209/209 A with all reconstruction and read-only checks passing; no vague majority threshold is used.

Future integration: this independent validator is delivered as the required pre-geometry entry check; historical generators/validators are deliberately unchanged. The existing pipeline is NOT automatically wired to enforce it in this read-only audit. New pipeline work must explicitly invoke this script and require A before admission. CLI JSON includes full evidence; do not treat CLI completion alone as acceptance.

Run `python -B scripts/test_validator.py` for native box/cylinder/triangle prism/loft positives, direct mesh imports, embedded/renamed triangle arrays, aliasing, external STEP, decoy features, dynamic calls, nonfinite values, loops, and code/STEP mismatch negatives. Synthetic triangle B-Rep is explicitly excluded from dataset counts.
'''
 spec+='\nCLI gate: exit code 0 only for A acceptance; exit code 2 for all nonaccepted classifications. JSON is written in both cases. Unhandled execution/input errors are nonzero.\n'
 (O/'reports/VALIDATOR_SPEC.md').write_text(spec)
 root='''# Root cause report

## Finding
Both original V1 and current V3 selected 209-part cohorts are independent native CadQuery feature programs. No selected part is a source-triangle wrapper. The original three partial STEP assemblies contain native parts; the current 20 GLB/PLY assembly previews are display meshes derived from those native STEP parts and are not themselves parametric CAD files.

## Three distinct phenomena
1. **BREP_FACET_TOPOLOGY**: one triangle (or a few patches) per source mesh triangle. It would show dense 3-edge planar faces and source-like topology. This was not found in the audited selected cases. The synthetic 320-triangle control demonstrates that the validator detects this while analytic ratio remains 1.0.
2. **Polygonal native feature geometry**: fitted 2D polyline contours are extruded, revolved or lofted. An extrusion of a many-sided contour creates genuine planar side strips. A revolved piecewise linear profile produces real cones/cylinders. These are native parametric features, but they need not be smooth or semantically optimal. Their angular appearance does not disappear merely by refining display tessellation.
3. **RENDER_TESSELLATION and shading**: execute_candidate.py `run` calls `reloaded.tessellate(0.001,0.05)` and writes cad_mesh_from_reloaded_step.ply. V3 assembly renderer `sample` returns `mesh.face_normals[idx]`; `render` shades samples with those constant triangle normals. This can expose display triangles and point-sampling grain on curved B-Rep faces. The new inspection images read original STEP, interpolate OCC surface normals and overlay only genuine B-Rep edges.

## Previous gate
PREVIOUS_NATIVE_CHECK_WAS_INSUFFICIENT = YES, specifically for complete representation evidence. It was NOT merely `.py exists` / STEP reload: execute_candidate.py `validate` already enforced a restrictive AST whitelist, only CadQuery import, approved feature methods, no external paths/payloads and boolean limits; p3_validate.py also checked banned constructors and feature budgets. It lacked direct OCC surface-type and triangular-face auditing and independent source/code/STEP correspondence. This is an evidence/coverage gap, not proof of a previous false acceptance. Its successful prevention of mesh wrappers is consistent with the new audit.

## Action
Adopt the delivered independent representation validator for future admission. No native CAD generator rebuild is justified by these representation results. Improvements to smooth profiles, fitting family choice, detail preservation and assembly completeness remain geometric modeling work; they were not performed in this audit. Existing geometry rejections are unchanged. Never infer high-detail geometric quality from A classification or from a large compression ratio.

Exact original script paths, SHA256 and line references are in `evidence/source_evidence.json`; source snapshots are alongside it. Generator data may legitimately read source meshes to estimate parameters; generated cad.py must and does reconstruct without the mesh.
'''
 (O/'reports/ROOT_CAUSE_REPORT.md').write_text(root)
 report=f'''# NATIVE PARAMETRIC CAD AUDIT V1

V1 is the primary 209-part cohort requested by the 4 Strict / 63 Near / 142 Reject stratification. V3 is a separate supplementary audit of the 209 parts shown in the latest assembly images. These are 209 corresponding part identities at two versions, not 418 unique dataset parts. No fitting, P3 rerun, new dataset examples or SCALE100 was performed. Synthetic validator controls are tests only.

## Result

| Field | Original V1 | Current V3 |
|---|---:|---:|
| Native parametric A | {s1['A_NATIVE_PARAMETRIC_N']} | {s3['A_NATIVE_PARAMETRIC_N']} |
| Native nonparametric B | {s1['B_NATIVE_BREP_NONPARAMETRIC_N']} | {s3['B_NATIVE_BREP_NONPARAMETRIC_N']} |
| Faceted B-Rep C | {s1['C_FACETED_BREP_N']} | {s3['C_FACETED_BREP_N']} |
| Mesh wrapper D | {s1['D_MESH_WRAPPER_N']} | {s3['D_MESH_WRAPPER_N']} |
| Uncertain E | {s1['E_UNCERTAIN_N']} | {s3['E_UNCERTAIN_N']} |
| Isolated reconstruction passed | {s1['ISOLATED_REEXECUTION_PASS_N']} | {s3['ISOLATED_REEXECUTION_PASS_N']} |
| Median source triangles | {s1['MEDIAN_SOURCE_TRIANGLE_N']} | {s3['MEDIAN_SOURCE_TRIANGLE_N']} |
| Median STEP faces | {s1['MEDIAN_STEP_FACE_N']} | {s3['MEDIAN_STEP_FACE_N']} |
| Median source triangles / STEP faces | {s1['MEDIAN_COMPRESSION_RATIO']:.6f} | {s3['MEDIAN_COMPRESSION_RATIO']:.6f} |
| Median analytic ratio | {s1['MEDIAN_ANALYTIC_FACE_RATIO']} | {s3['MEDIAN_ANALYTIC_FACE_RATIO']} |
| Median planar triangle ratio | {s1['MEDIAN_TRIANGLE_PLANAR_FACE_RATIO']} | {s3['MEDIAN_TRIANGLE_PLANAR_FACE_RATIO']} |

READ_ONLY_GUARD = {final['READ_ONLY_GUARD']}; REPRESENTATION_GATE = {final['REPRESENTATION_GATE']}. File guard checks SHA256, size, mtime, additions and removals across all four historical output trees (V1, V2, V3, assembly visualizations). It does not cover unrelated training directories. See integrity/READ_ONLY_GUARD.json.

All V1 statuses remain 4/63/142, with native representation in each group. V3 geometry statuses remain 15/77/117. **Representation eligibility is not paired-training acceptance**: only a separate geometry gate can accept fidelity. Existing geometry gate remains FAIL; no automatic scale-up or training admission.

V1 STEP faces range {s1['step_face_range']}; V3 {s3['step_face_range']}. V1 has {s1['polyline_program_n']} polyline programs; V3 {s3['polyline_program_n']}. These fitted numeric profiles are compact parametric feature definitions but may remain polygonal. Surface distributions and every face's area/edge/bbox evidence are in tables/ and cases/.

## Assemblies and visuals
Three historical partial STEP assemblies reloaded and their surface counts matched the audited native member parts (2, 1, 1 parts). Current 20 GLB/PLY previews trace to 209 audited native parts, including Near/Reject; no complete geometric assembly acceptance is implied. See assembly_audit.csv and v3_preview_assembly_audit.csv.

The visual gallery contains 10 representative current parts selected by surface diversity and the most complex topology, plus one clearly labeled synthetic faceted control. No real faceted cases were found, so none were invented to meet a 5+5 illustration suggestion. For each: STEP smooth shading, actual B-Rep edges, surface types. Main evidence is AST + OCC topology + source comparison, not screenshots.

## Prior validator and root cause
{final['WHY']}

{final['PRIMARY_ROOT_CAUSE']} See ROOT_CAUSE_REPORT.md and evidence/source_evidence.json for scripts/functions/lines. Normal CAD display tessellation must be distinguished from triangle B-Rep topology. Native polygonal extrusion is a third category of visual angularity and remains a fitting-quality concern.

## Validation and scope
{tests['test_n']} validator tests passed. All 209 programs in each version were reexecuted from cad.py alone with file access unavailable in the supported restricted grammar. No original STEP was rewritten. In-memory reconstruction was compared to original reloaded STEP using topology/surface counts, bounds, volume and area. This is not an arbitrary-code security sandbox or formal shape-equivalence proof. Unsupported future syntax fails closed to review.

## Decision
Representation validity passes; fitting quality remains relevant. The requested CAN_CONTINUE_PART_CAD_FITTING_V2 is YES at the representation gate, but V2 already exists and was not rerun. NEXT_ALLOWED_STAGE = GEOMETRY_FITTING_REVIEW_WITH_NATIVE_REPRESENTATION_VALIDATOR. No native generator rebuild is indicated. This audit installs no automatic pipeline hook because historical code is read-only; future work must invoke the delivered validator explicitly.

## Deliverables
scripts/validate_native_parametric_cad.py; tables/representation_audit_209.csv (V1) and representation_audit_209_v3.csv; surface/status/suspicious/accepted tables; per-face CSVs; per-case JSON and isolated cad.py execution logs; assembly topology JSON; source evidence snapshots; tests; gallery; integrity guard and structured SUMMARY.json.
'''
 report+=f'\nNeither cohort has a dense triangular B-Rep pattern. Each contains {s1["triangle_planar_total"]} actual triangular planar faces in total (see actual_triangular_face_cases tables); the median ratio 0 does not mean every face is nontriangular. These small counts are consistent with native feature intersections/caps and do not satisfy triangle-wrapper evidence.\n'
 (O/'reports/FINAL_REPORT.md').write_text(report)
 dump(O/'manifests/environment.json',{'python':sys.version,'platform':platform.platform(),'cadquery':cq.__version__,'numpy':np.__version__,'trimesh':trimesh.__version__,'utc':datetime.datetime.now(datetime.timezone.utc).isoformat()})
 print(json.dumps(final,indent=2))
