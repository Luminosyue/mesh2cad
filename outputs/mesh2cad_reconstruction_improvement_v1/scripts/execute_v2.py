"""Restricted native CQ execution. Writes only to a fresh supplied output directory."""
import ast, json, sys, hashlib, traceback
from pathlib import Path
import numpy as np
import cadquery as cq
import trimesh

ALLOWED_ATTRS = {'Plane', 'Workplane', 'polyline', 'close', 'extrude', 'cut', 'union', 'box', 'circle', 'sphere', 'workplane', 'loft', 'revolve'}
ALLOWED_NODES = (ast.Module, ast.Import, ast.alias, ast.Assign, ast.Name, ast.Store, ast.Load,
                 ast.Call, ast.Attribute, ast.keyword, ast.Constant, ast.List, ast.Tuple,
                 ast.UnaryOp, ast.USub)

def validate(code):
    tree = ast.parse(code)
    boolean_n=sum(isinstance(n,ast.Call) and isinstance(n.func,ast.Attribute) and n.func.attr in {'union','cut','intersect'} for n in ast.walk(tree))
    if boolean_n>6: raise ValueError('Boolean budget exceeded')
    assigned = {'cq'}
    for node in ast.walk(tree):
        if not isinstance(node, ALLOWED_NODES):
            raise ValueError('Disallowed AST: ' + type(node).__name__)
        if isinstance(node, ast.Import) and not (len(node.names)==1 and node.names[0].name=='cadquery' and node.names[0].asname=='cq'):
            raise ValueError('Only import cadquery as cq is permitted')
        if isinstance(node, ast.Attribute) and node.attr not in ALLOWED_ATTRS:
            raise ValueError('Disallowed CAD operation: ' + node.attr)
        if isinstance(node, ast.Name) and ('__' in node.id or node.id in {'vertices','faces','mesh','open','eval','exec'}):
            raise ValueError('Disallowed name')
        if isinstance(node, ast.Call) and not isinstance(node.func, ast.Attribute):
            raise ValueError('Only native CQ calls are permitted')
        if isinstance(node, ast.Constant) and isinstance(node.value, str) and node.value not in {'XY'}:
            raise ValueError('No embedded paths or payloads')
        if isinstance(node, ast.Assign):
            if len(node.targets)!=1 or not isinstance(node.targets[0], ast.Name):
                raise ValueError('Only simple assignments')
            assigned.add(node.targets[0].id)
    if 'result' not in assigned or len(code)>60000:
        raise ValueError('Missing result or excessive program size')
    return tree

def bbox(s):
    b=s.BoundingBox()
    return [[b.xmin,b.ymin,b.zmin],[b.xmax,b.ymax,b.zmax]]

def run(program, out):
    out.mkdir(exist_ok=False)
    r=dict(parse_pass=False,native_pass=False,execute_pass=False,shape_nonempty=False,
           step_export_pass=False,step_reload_pass=False,failure_reason=None)
    phase='CAD_SYNTAX_FAILURE'
    try:
        code=program.read_text(); tree=validate(code)
        r.update(parse_pass=True,native_pass=True,program_sha256=hashlib.sha256(code.encode()).hexdigest())
        phase='BOOLEAN_FAILURE' if '.cut(' in code or '.union(' in code else 'CAD_EXECUTION_FAILURE'
        scope={}; exec(compile(tree,str(program),'exec'),scope)
        shape=scope['result'].val()
        r['shape_nonempty']=bool(len(shape.Faces()))
        if not r['shape_nonempty'] or not shape.isValid() or not shape.Solids():
            raise ValueError('Result must be a valid nonempty solid B-Rep')
        r['execute_pass']=True
        phase='STEP_EXPORT_FAILURE'
        step=out/'cad.step'; cq.exporters.export(shape,str(step))
        r['step_export_pass']=step.exists() and step.stat().st_size>0
        if not r['step_export_pass']: raise ValueError('Empty export')
        phase='STEP_RELOAD_FAILURE'
        reloaded=cq.importers.importStep(str(step)).val()
        bounds=np.asarray(bbox(reloaded))
        r.update(reload_solid_count=len(reloaded.Solids()),reload_face_count=len(reloaded.Faces()),
                 reload_edge_count=len(reloaded.Edges()),reload_bbox=bounds.tolist(),reload_valid=reloaded.isValid())
        if not reloaded.isValid() or not reloaded.Solids() or not np.isfinite(bounds).all() or np.any(bounds[1]<=bounds[0]):
            raise ValueError('Reloaded shape invalid or empty')
        r['step_reload_pass']=True
        phase='INVALID_CAD_TESSELLATION'
        verts,faces=reloaded.tessellate(0.001,0.05)
        mesh=trimesh.Trimesh(vertices=[v.toTuple() for v in verts],faces=faces,process=True)
        if not len(mesh.faces) or not np.isfinite(mesh.vertices).all() or mesh.area<=0:
            raise ValueError('Invalid reloaded tessellation')
        mesh.export(out/'cad_mesh_from_reloaded_step.ply')
        r.update(tessellation_pass=True,tessellation_source='RELOADED_STEP',
                 step_sha256=hashlib.sha256(step.read_bytes()).hexdigest(),
                 cad_mesh_sha256=hashlib.sha256((out/'cad_mesh_from_reloaded_step.ply').read_bytes()).hexdigest())
    except Exception as e:
        r.update(failure_reason=phase,error=str(e),traceback=traceback.format_exc())
    (out/'execution.json').write_text(json.dumps(r,indent=2,allow_nan=False))
    return r

if __name__=='__main__':
    print(json.dumps(run(Path(sys.argv[1]),Path(sys.argv[2]))))
