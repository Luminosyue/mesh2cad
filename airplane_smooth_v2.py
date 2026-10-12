import os
os.environ.update(OPENBLAS_NUM_THREADS='1', OMP_NUM_THREADS='1', MKL_NUM_THREADS='1')
import json, sys, time, subprocess, shutil
from pathlib import Path
import cadquery as cq

BASE = Path('/data/home/cuiyuehan/project/mesh2cad')
OLD = BASE/'p3_xpart_high_fidelity_air_tank_v1/cases/airplane'
OUT = BASE/'p3_xpart_smooth_airplane_v2'

TEMPLATE = '''import time, json
from pathlib import Path
import cadquery as cq

PARAMETERS = {parameters!r}

def build_model():
    p = PARAMETERS
    wires = []
    for sec in p['sections']:
        plane = cq.Plane(origin=tuple(p['origin'][i]+p['normal'][i]*sec['z'] for i in range(3)), xDir=tuple(p['xdir']), normal=tuple(p['normal']))
        wires.append(cq.Workplane(plane).spline([tuple(x) for x in sec['points']], periodic=True).close().val())
    return cq.Solid.makeLoft(wires, False)

if __name__ == '__main__':
    out = Path(__file__).resolve().parent
    t = time.time()
    print('BUILD_START', flush=True)
    shape = build_model()
    print('BUILD_DONE', time.time()-t, flush=True)
    valid = bool(shape.isValid())
    print('VALIDATED', valid, len(shape.Faces()), flush=True)
    cq.exporters.export(shape, str(out/'reconstructed.step'))
    print('STEP_DONE', time.time()-t, flush=True)
    b = shape.BoundingBox()
    (out/'geometry.json').write_text(json.dumps(dict(valid=valid, solids=len(shape.Solids()), faces=len(shape.Faces()), elapsed=time.time()-t, bbox=[b.xmin,b.ymin,b.zmin,b.xmax,b.ymax,b.zmax]), indent=2))
'''

def run_geometry():
    OUT.mkdir(parents=True, exist_ok=True)
    results = []
    for old in sorted(OLD.glob('PART_*')):
        d = json.loads((old/'metrics.json').read_text())
        if '/xpart_parts/' not in d['source_path']:
            continue
        dest = OUT/'parts'/old.name
        dest.mkdir(parents=True, exist_ok=True)
        p = json.loads((old/'parameters.json').read_text())
        (dest/'cad.py').write_text(TEMPLATE.format(parameters=p))
        shutil.copy2(old/'parameters.json', dest/'parameters.json')
        shutil.copy2(old/'metrics.json', dest/'original_metrics.json')
        if not (dest/'geometry.json').exists():
            with (dest/'build.log').open('w') as f:
                try:
                    r = subprocess.run([sys.executable, '-u', 'cad.py'], cwd=dest, stdout=f, stderr=subprocess.STDOUT, timeout=180)
                    if r.returncode:
                        print('FAILED', old.name, r.returncode, flush=True)
                        continue
                except subprocess.TimeoutExpired:
                    print('TIMEOUT', old.name, flush=True)
                    continue
        g=json.loads((dest/'geometry.json').read_text())
        results.append(dict(part=old.name,**g))
        print('GEOMETRY',old.name,g,flush=True)
    (OUT/'geometry_summary.json').write_text(json.dumps(results,indent=2))

if __name__=='__main__':
    run_geometry()
