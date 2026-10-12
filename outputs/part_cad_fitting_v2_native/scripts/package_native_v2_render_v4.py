from v2_common import *
import zipfile
R=O.parent/'cad_render_v4';validation=read(O/'integrity/FINAL_VALIDATION.json');assert validation['pass']
readme='''# PART_CAD_FITTING_V2_NATIVE_AND_RENDER_V4

Read part_cad_fitting_v2_native/reports/PART_CAD_FITTING_V2_NATIVE_REPORT.md and reports/SUMMARY.json. Original V1 is the paired 4/63/142 reference. Prior V3 improvements are preserved and separately attributed; this round is not a relabeling of those gains.

Fitting entry: scripts/run_part_cad_fitting_v2_native.py --phase near --workers 12; only after reports/NEAR_GATE.json permits it, use --phase reject --workers 12. Candidate jobs resume completed records. All final geometry gates use frozen original source/seed/evaluator. Numerical proposals and proxy search traces are retained.

Renderer entry: cad_render_v4/scripts/render_v4_assemblies.py. Run under xvfb-run with TMPDIR set to cad_render_v4/runtime. It renders unchanged historical V3 STEP, not newly fitted outputs, so display improvements are isolated from geometry improvements. Evaluation tessellation is never replaced with display tessellation.

Environment: /data/miniconda3/envs/cadfit-env/bin/python -B on the original server. Dependencies: CadQuery/OCP, NumPy, scipy, shapely, trimesh, VTK, Pillow and Xvfb. Paths are pinned to the original dataset. Input copies and selected native programs are included. Running preparation again in a completed output directory is intentionally refused.

Validation scripts: test_native_profiles.py; prepare_native_v2.py --verify (historical hashes); report_native_v2.py; visualize_native_v2.py under Xvfb; validate_native_v2_delivery.py. Never overwrite the historical V1/V2/V3/audit directories. No training, scale-up, source change, P3 rerun or assembly optimization was performed.

Open cad_render_v4/index.html for 20 unchanged-geometry V3/V4 render comparisons. Open part_cad_fitting_v2_native/visualizations/index.html for 30 source/V1/new CAD/overlay comparisons. Each category is labeled; inherited rescues are not claimed as new.
'''
(O/'README.md').write_text(readme)
excluded={'PART_CAD_FITTING_V2_NATIVE_AND_RENDER_V4_DELIVERY.zip','DELIVERY_SHA256.json','ARTIFACT_SHA256.json','package.log'}
files=[p for root in [O,R] for p in root.rglob('*') if p.is_file() and p.name not in excluded and 'runtime' not in p.relative_to(root).parts and '__pycache__' not in p.parts]
dump(O/'ARTIFACT_SHA256.json',{str(p.relative_to(O.parent)):sha(p) for p in sorted(files)})
z=O/'PART_CAD_FITTING_V2_NATIVE_AND_RENDER_V4_DELIVERY.zip'
with zipfile.ZipFile(z,'w',zipfile.ZIP_DEFLATED,compresslevel=5) as archive:
 for p in sorted(files)+[O/'ARTIFACT_SHA256.json']:archive.write(p,str(p.relative_to(O.parent)))
with zipfile.ZipFile(z) as archive:assert archive.testzip() is None
meta={'path':str(z),'bytes':z.stat().st_size,'sha256':sha(z),'file_n':len(files)+1,'validation':validation};dump(O/'DELIVERY_SHA256.json',meta);print(json.dumps(meta,indent=2))
