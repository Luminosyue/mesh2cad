"""Test evenly spaced, regularized section grids for an already freshly fitted part."""
from regenerate_smooth import *
from copy import deepcopy
from scipy.interpolate import PchipInterpolator
def regularize(spec,sigma):
    spec=deepcopy(spec)
    tracks=[f['sections'] for f in spec['features']]+spec.get('hole_tracks',[])
    for track in tracks:
        if len(track)<4 or any(s['outer']['kind']!='spline' for s in track):continue
        zs=np.array([s['z'] for s in track]);uniform=np.linspace(zs[0],zs[-1],len(zs))
        for key,hi in [('outer',None)]+[('holes',i) for i in range(len(track[0]['holes']))]:
            sketches=[s[key] if hi is None else s[key][hi] for s in track]
            if any(sk['kind']!='spline' for sk in sketches):continue
            xy=np.array([sk['points'] for sk in sketches]);xy=PchipInterpolator(zs,xy,axis=0)(uniform)
            xy=gaussian_filter1d(xy,sigma,axis=0,mode='nearest')
            xy=gaussian_filter1d(xy,.4,axis=1,mode='wrap')
            for sk,p in zip(sketches,xy):sk['points']=p.tolist()
        for s,z in zip(track,uniform):s['z']=float(z)
    spec['regularization']='uniform z sections with PCHIP resampling and Gaussian profile regularization'
    spec['regularization_sigma']=sigma;spec.pop('partition_final',None)
    return spec
def main():
    case,part=sys.argv[1:3];base=OUT/'cases'/case/part;od=OUT/'regularized_trials'/case/part;od.mkdir(parents=True,exist_ok=True)
    report=json.loads((base/'report.json').read_text());original=json.loads((base/'parameters.json').read_text())
    if original['method'] not in ('smooth_loft','tracked_smooth_loft'):return
    source=load(report['source_path']);center=np.array(original['center']);scale=original['construction_scale'];m=source.copy();m.apply_translation(-center);m.apply_scale(scale)
    np.savez_compressed(od/'evaluation_mesh.npz',vertices=m.vertices,faces=m.faces);best=None
    for sigma in (.4,.8,1.3):
        spec=regularize(original,sigma);dump(od/'candidate_parameters.json',spec)
        try:
            rr=subprocess.run([sys.executable,str(SCRIPTS/'build_native_candidate.py'),str(od/'candidate_parameters.json'),str(od/'native_candidate.brep'),str(od/'evaluation_mesh.npz'),str(od/'candidate_quality.json')],capture_output=True,text=True,timeout=45)
            if rr.returncode:print(rr.stderr[-500:],flush=True);continue
            q=json.loads((od/'candidate_quality.json').read_text());print(sigma,q,flush=True)
            if best is None or score(q)<best[0]:best=(score(q),spec,cq.Shape.importBrep(str(od/'native_candidate.brep')),(od/'candidate_runtime.txt').read_text())
        except Exception as e:print(str(e),flush=True)
    if best is None:return
    _,spec,body,runtime=best;ns={};exec(runtime,ns);body=ns['partition_periodic_faces'](body);spec['partition_final']=True
    world=body.scale(1/scale).translate(tuple(center));world.exportStep(str(od/'model.step'));world.exportBrep(str(od/'model.brep'))
    actual=cq.importers.importStep(str(od/'model.step')).val();cm=tess(actual.translate(tuple(-center)).scale(scale),.025);q=evaluate(m,cm,10000);cm.apply_scale(1/scale);cm.apply_translation(center);cm.export(od/'model.stl')
    dump(od/'parameters.json',spec);(od/'cad.py').write_text(runtime+'\nPARAMETERS = '+repr(spec)+'\n\nif __name__ == "__main__":\n    from pathlib import Path\n    p=Path(__file__).parent\n    shape=build_model(PARAMETERS)\n    assert shape.isValid() and shape.Solids()\n    shape.exportStep(str(p/"model.step"))\n    shape.exportBrep(str(p/"model.brep"))\n    shape.exportStl(str(p/"model.stl"),tolerance=0.025,angularTolerance=0.15)\n')
    report.update(quality=q,status='ACCEPTED' if passed(q) else 'NEEDS_REFINEMENT',cad_faces=len(actual.Faces()),cad_solids=len(actual.Solids()),regularization=spec['regularization'])
    from smooth_visualize import extract_and_render
    report.update(**extract_and_render(actual,cm,od,report,source));dump(od/'report.json',report);print('FINAL',q,report['status'],flush=True)
if __name__=='__main__':main()
