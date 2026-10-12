import json,sys,runpy,traceback
from pathlib import Path
import cadquery as cq
import numpy as np
import trimesh
from scipy.spatial import cKDTree

folder=Path(sys.argv[1]); meta=json.loads(Path(sys.argv[2]).read_text())
try:
    ns=runpy.run_path(str(folder/'cadquery.py'))
    obj=next((ns[k] for k in ['r','result','shape'] if k in ns),None)
    if obj is None: raise ValueError('No CAD result')
    if isinstance(obj,cq.Workplane):
        vals=obj.vals(); shape=cq.Compound.makeCompound(vals) if len(vals)>1 else vals[0]
    else:shape=obj
    assert shape.isValid(),'Invalid generated BRep'
    assert len(shape.Solids())>0,'No solid in generated BRep'
    placed=shape.scale(meta['world_scale']).translate(tuple(meta['center']))
    assert placed.isValid(),'Invalid world BRep'
    cq.exporters.export(placed,str(folder/'world.step'))
    reloaded=cq.importers.importStep(str(folder/'world.step')).val()
    assert reloaded.isValid() and reloaded.Solids(),'STEP reload failed'
    verts,faces=placed.tessellate(max(meta['extent']*0.001,1e-6),0.1)
    mesh=trimesh.Trimesh([v.toTuple() for v in verts],faces,process=False)
    mesh.export(folder/'world.stl')
    src=trimesh.load(meta['input_stl'],force='mesh')
    np.random.seed(0)
    p,_=trimesh.sample.sample_surface(mesh,2048);q,_=trimesh.sample.sample_surface(src,2048)
    a=cKDTree(p).query(q)[0];b=cKDTree(q).query(p)[0]
    cd=float((np.square(a).mean()+np.square(b).mean())/meta['extent']**2)
    result=dict(status='PASS',valid=True,solids=len(placed.Solids()),faces=len(placed.Faces()),volume=placed.Volume(),normalized_chamfer_squared=cd,bounds=mesh.bounds.tolist(),world_step=str(folder/'world.step'))
except Exception:
    result=dict(status='FAIL',error=traceback.format_exc())
(folder/'EXECUTION.json').write_text(json.dumps(result,indent=2))
print(json.dumps(result))
