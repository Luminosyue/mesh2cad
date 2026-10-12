"""Supplement final report with artifact replay, candidate failures and inventory statistics."""
import json,csv,collections
from pathlib import Path
import numpy as np
import trimesh
from factory import ROOT,SEED,load,evaluate,write,sha

rows=[json.loads(p.read_text()) for p in sorted((ROOT/'cases').glob('*/manifest.json'))]
if len(rows)!=100: raise RuntimeError('Expected the completed frozen 100-case run')
counts=collections.Counter()
candidate_rows=[]
raw_audits=[]
for r in rows:
    raw=trimesh.load(r['source_mesh_path'],force='mesh',process=False)
    raw_ok=bool(len(raw.vertices)>0 and len(raw.faces)>0 and np.isfinite(raw.vertices).all()
                and raw.faces.min()>=0 and raw.faces.max()<len(raw.vertices))
    raw_audits.append({'case_id':r['case_id'],'process':False,'raw_vertex_count':len(raw.vertices),
        'raw_face_count':len(raw.faces),'finite_and_valid':raw_ok,
        'face_count_preserved':len(raw.faces)==r.get('source_audit',{}).get('face_count')})
    for a in r['attempts']:
        reason=a.get('failure_reason') or a['execution'].get('failure_reason')
        if not reason and a.get('metrics') and not a['metrics']['strict_pass']:reason='GEOMETRY_MISMATCH'
        if reason:counts[reason]+=1
        candidate_rows.append({'case_id':r['case_id'],'attempt_index':a['attempt_index'],'kind':a['kind'],
            'failure_reason':reason,'step_reload_pass':a['execution'].get('step_reload_pass',False),
            'strict_pass':a.get('metrics',{}).get('strict_pass',False),'selected':a['attempt_index']==r.get('selected_attempt_index')})
with (ROOT/'tables/candidate_outcomes_v2.csv').open('x',newline='') as f:
    w=csv.DictWriter(f,fieldnames=list(candidate_rows[0]));w.writeheader();w.writerows(candidate_rows)
replays=[]
for r in rows[:3]:
    d=ROOT/'cases'/r['case_id'];src=load(d/'normalized/normalized_mesh.ply');cad=load(r['cad_mesh_path'])
    metric=evaluate(src,cad,SEED+int(r['case_id'].split('_')[1])*10)
    errors={k:abs(metric[k]-r['geometry_metrics'][k]) for k in ['chamfer_mean','chamfer_p95','normalized_chamfer','iou','bbox_error','centroid_l2_error']}
    raw=load(r['source_mesh_path']);v=np.asarray(raw.vertices);f=np.asarray(r['normalization']['forward_transform']);inv=np.asarray(r['normalization']['inverse_transform'])
    homogeneous=np.column_stack([v,np.ones(len(v))]);back=(homogeneous@f.T)@inv.T
    replays.append({'case_id':r['case_id'],'metric_absolute_differences':errors,'coordinate_roundtrip_max_error':float(np.max(np.abs(back[:,:3]-v))),
                    'pass':bool(max(errors.values())<1e-12 and np.max(np.abs(back[:,:3]-v))<1e-10)})
summary={'candidate_n':len(candidate_rows),'candidate_failure_counts':dict(counts),
    'parent_object_n':len({r['parent_object_id'] for r in rows}),
    'exact_source_hash_n':len({r['source_mesh_sha256'] for r in rows}),
    'source_watertight_n':sum(r.get('source_audit',{}).get('watertight',False) for r in rows),
    'surface_cache_status':'NOT_BUILT','curve_cache_status':'NOT_BUILT','canary_artifact_replays':replays,
    'raw_source_audits':raw_audits,
    'pass':all(r['pass'] for r in replays) and all(r['finite_and_valid'] and r['face_count_preserved'] for r in raw_audits)}
write(ROOT/'reports/delivery_checks_v2.json',summary)
hashes={str(p.relative_to(ROOT)):sha(p) for name in ['scripts','config'] for p in (ROOT/name).glob('*') if p.is_file()}
write(ROOT/'integrity/FINAL_CODE_CONFIG_SHA256.json',hashes)
notes='''# Reproduce this frozen Smoke100

Use the recorded server environment:

```sh
PY=/data/miniconda3/envs/cadfit-env/bin/python
OLD=/data/home/cuiyuehan/project/mesh2cad/outputs/mesh2cad_data_factory_v1_smoke100
NEW=/data/home/cuiyuehan/project/mesh2cad/outputs/mesh2cad_data_factory_v1_smoke100_replay
PYTHONDONTWRITEBYTECODE=1 "$PY" -B "$OLD/scripts/bootstrap.py" --output-root "$NEW"
cd "$NEW"
PYTHONDONTWRITEBYTECODE=1 "$PY" -B scripts/factory.py --limit 3
PYTHONDONTWRITEBYTECODE=1 "$PY" -B scripts/factory.py --limit 10
PYTHONDONTWRITEBYTECODE=1 "$PY" -B scripts/factory.py --limit 100
PYTHONDONTWRITEBYTECODE=1 "$PY" -B scripts/validate_and_report.py final
```

Bootstrap requires a never-used direct child of the project's outputs directory and refuses existing paths. This command sequence was not run a second time: the actual run used 3 → 10 → 100 once, preserving the same source selection, code and evaluator. The bootstrap copy helper is supplied for reproducibility. The historic source tree must remain present and match its hashes; the local delivery copy is an inspection bundle, not a self-contained replacement for that tree or the Python environment.

The run is capped at 100. SCALE_1000 is a next-stage readiness decision only, not an instruction executed by these files. It needs a new output root and a reviewed larger source inventory/configuration. The same group-safe provenance, program, reload, evaluator and integrity gates must remain in force.

Surface and curve caches were intentionally left NOT_BUILT because no cache extractor/schema was validated in this factory; no placeholder geometry is supplied. These optional caches do not affect the execution or geometry gate.

Runtime note: subdivision voxelization of long narrow triangles can have high transient memory use. One observed worker reached about 19 GiB RSS on this server (about 0.9 TiB RAM). The four-worker setting was used on this server; do not assume the same concurrency is appropriate on a small-memory host. This is an observed portability limitation, not a geometry score adjustment.

Final case failures and candidate failures have different denominators: the former count each source once after selection; the latter retain every attempted hypothesis. `candidate_outcomes_v2.csv` records that distinction. The three canary cases have also been reevaluated from their final serialized artifacts to check exact deterministic metric replay and coordinate round trips; see `reports/delivery_checks_v2.json`.

The first supplemental delivery check hit a NumPy boolean JSON serialization error after evaluating the artifacts. Its incomplete `reports/delivery_checks.json` and log are preserved for traceability and are superseded by `reports/delivery_checks_v2.json`. The correction converts the diagnostic boolean to Python bool; it changes no source, CAD, metric, filter decision or frozen core script. The authoritative supplemental entrypoint is `scripts/delivery_checks_v2.py`; packaging uses `scripts/package_delivery_v2.py`.
'''
(ROOT/'README_REPRODUCE.md').write_text(notes)
print(json.dumps(summary))
