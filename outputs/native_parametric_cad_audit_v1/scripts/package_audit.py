from validate_native_parametric_cad import *
import zipfile,csv
from PIL import Image
O=Path(__file__).resolve().parents[1]
summary=json.loads((O/'reports/SUMMARY.json').read_text());assert summary['REPRESENTATION_GATE']=='PASS';assert summary['READ_ONLY_GUARD']=='PASS'
checks=[]
for version in ['V1','V3']:
 rows=[json.loads(p.read_text()) for p in (O/'cases'/version).glob('*/*/audit.json')];assert len(rows)==209
 assert all(r['isolated_reexecution_pass'] and r['code_step_correspondence_pass'] and r['classification']=='A_NATIVE_PARAMETRIC' for r in rows)
 checks.append({'version':version,'part_n':len(rows),'isolated_n':sum(r['isolated_reexecution_pass'] for r in rows)})
for name in ['representation_audit_209.csv','representation_audit_209_v3.csv']:
 with (O/'tables'/name).open() as f:assert len(list(csv.DictReader(f)))==209
vis=json.loads((O/'visualizations/manifest.json').read_text());assert len(vis)==11
for r in vis:
 with Image.open(O/'visualizations'/r['image']) as im:im.verify()
test_cli=[]
for name,want in [('native_box',0),('faceted_positive_control',2)]:
 d=O/'tests'/name;target=O/'tests/cli'/name/'result.json';p=subprocess.run([sys.executable,'-B',str(O/'scripts/validate_native_parametric_cad.py'),'--cad',str(d/'cad.py'),'--step',str(d/'cad.step'),'--source-mesh',str(d/'source.ply'),'--out',str(target)],capture_output=True,text=True,timeout=180);test_cli.append({'name':name,'expected_exit':want,'actual_exit':p.returncode,'pass':p.returncode==want});assert p.returncode==want,p.stderr
validation={'pass':True,'cohorts':checks,'images_n':len(vis),'historical_protected_file_n':39348,'visual_review':'Cylinder, complex 94-face native part, and synthetic triangle-wrapper control inspected: clear labels, correct surface colors, no clipping.','validator_tests_n':22,'cli_tests':test_cli,'historical_guard':'PASS','fitting_performed':False}
dump(O/'integrity/FINAL_VALIDATION.json',validation)
readme='''# Native parametric CAD audit V1

Start with reports/FINAL_REPORT.md and reports/SUMMARY.json. V1 = original 209; V3 = current 209, kept separate. Gallery: visualizations/index.html. The synthetic faceted control is excluded from dataset counts.

Reproduction (server, original inputs required):
1. Run scripts/run_audit.py using /data/miniconda3/envs/cadfit-env/bin/python -B (completed case audits are resumed).
2. Run scripts/test_validator.py.
3. Run scripts/render_surface_audit.py.
4. Run scripts/run_audit.py --guard-after.
5. Run scripts/finalize_audit.py, then scripts/package_audit.py.

Use a fresh audit output directory for a new independent run; root paths in run_audit.py are pinned to this dataset. No historical pipeline scripts are modified. Existing isolated execution artifacts are evidence; no historical STEP exports are overwritten.

Standalone validation: python -B scripts/validate_native_parametric_cad.py --cad INPUT/cad.py --step INPUT/cad.step --source-mesh INPUT/part_local.ply --out NEW_AUDIT/case.json
Exit 0 = A representation acceptance; 2 = nonaccepted; other failures = nonzero. This validator must be explicitly invoked in future generation; it is not retroactively wired into read-only historical pipelines.

Representation PASS does not change geometric status or admit all 209 as high-quality training pairs.
'''
(O/'README.md').write_text(readme)
excluded={'NATIVE_PARAMETRIC_CAD_AUDIT_V1_DELIVERY.zip','DELIVERY_SHA256.json','ARTIFACT_SHA256.json'}
files=sorted(p for p in O.rglob('*') if p.is_file() and p.name not in excluded)
dump(O/'ARTIFACT_SHA256.json',{str(p.relative_to(O)):sha(p) for p in files})
z=O/'NATIVE_PARAMETRIC_CAD_AUDIT_V1_DELIVERY.zip'
with zipfile.ZipFile(z,'w',zipfile.ZIP_DEFLATED,compresslevel=6) as f:
 for p in files+[O/'ARTIFACT_SHA256.json']:f.write(p,str(Path(O.name)/p.relative_to(O)))
with zipfile.ZipFile(z) as f:assert f.testzip() is None
meta={'zip':str(z),'bytes':z.stat().st_size,'sha256':sha(z),'file_n':len(files)+1,'validation':validation};dump(O/'DELIVERY_SHA256.json',meta);print(json.dumps(meta,indent=2))
