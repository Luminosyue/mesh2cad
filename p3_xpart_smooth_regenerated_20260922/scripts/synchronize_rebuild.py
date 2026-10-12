"""Make all artifacts agree with a verified standalone native reconstruction."""
from regenerate_smooth import *
from smooth_visualize import extract_and_render
case,part=sys.argv[1:3];base=OUT/'cases'/case/part;od=OUT/'repairs'/case/part;od.mkdir(parents=True,exist_ok=True)
backup=od/'before';backup.mkdir(exist_ok=True)
names=['model.step','model.brep','model.stl','cad.py','parameters.json','curves.json','curve_samples_256.npz','render_transform.json','surface_boundaries.png','source_vs_cad.png','report.json']
for name in names:
    if not (backup/name).exists():shutil.copy2(base/name,backup/name)
code=(base/'cad.py').read_text();line='    shape.exportStep(str(p/"model.step"))\n'
code=code.replace(line,line+'    shape=cq.importers.importStep(str(p/"model.step")).val()\n')
(od/'cad.py').write_text(code);subprocess.run([sys.executable,str(od/'cad.py')],cwd=od,check=True,timeout=120)
report=json.loads((base/'report.json').read_text());spec=json.loads((base/'parameters.json').read_text());source=load(report['source_path']);center=np.array(spec['center']);scale=spec['construction_scale']
assert hashlib.sha256(Path(report['source_path']).read_bytes()).hexdigest()==report['source_sha256']
actual=cq.importers.importStep(str(od/'model.step')).val();assert actual.isValid() and actual.Solids();actual.exportBrep(str(od/'model.brep'))
src=source.copy();src.apply_translation(-center);src.apply_scale(scale);cm=tess(actual.translate(tuple(-center)).scale(scale),.025);q=evaluate(src,cm,10000)
cm.apply_scale(1/scale);cm.apply_translation(center);cm.export(od/'model.stl');dump(od/'parameters.json',spec)
report.update(quality=q,status='ACCEPTED' if passed(q) else 'NEEDS_REFINEMENT',cad_faces=len(actual.Faces()),cad_solids=len(actual.Solids()),step_valid=True,rebuild_synchronized=True)
report.update(**extract_and_render(actual,cm,od,report,source));dump(od/'report.json',report)
for name in names:
    if name!='report.json':shutil.copy2(od/name,base/name)
dump(base/'report.json',report)
print(report['status'],q,flush=True)
