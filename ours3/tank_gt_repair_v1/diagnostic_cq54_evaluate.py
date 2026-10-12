import os
for k in ['OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS']:os.environ[k]='1'
from pathlib import Path
import sys,ast,json,resource
resource.setrlimit(resource.RLIMIT_CPU,(1800,1800));resource.setrlimit(resource.RLIMIT_AS,(24*1024**3,24*1024**3))
import cadquery as cq,numpy as np,trimesh
sys.path.insert(0,'/data/home/cuiyuehan/project/mesh2cad/p3_xpart_open_cases/_cadquery_batch_code_20260922')
from quality import tessellate,evaluate
dest,target=map(Path,sys.argv[1:3]);code=(dest/'prediction.py').read_text();tree=ast.parse(code)
allowed=(ast.Module,ast.Import,ast.alias,ast.Assign,ast.Name,ast.Load,ast.Store,ast.Call,ast.Attribute,ast.keyword,ast.List,ast.Tuple,ast.Constant,ast.UnaryOp,ast.USub,ast.Expr)
attrs={'Workplane','Plane','Location','polyline','close','extrude','union','fuse','cut','center','circle','spline','wire','val','newObject','toPending','loft','clean','located','scale','translate','moveTo','lineTo','revolve'}
for n in ast.walk(tree):
    assert isinstance(n,allowed),type(n).__name__
    if isinstance(n,ast.Import):assert len(n.names)==1 and n.names[0].name=='cadquery' and n.names[0].asname=='cq'
    if isinstance(n,ast.Name):assert not n.id.startswith('_')
    if isinstance(n,ast.Attribute):assert n.attr in attrs,n.attr
    if isinstance(n,ast.Call):assert isinstance(n.func,ast.Attribute)
def only_import(name,*args,**kwargs):
    if name!='cadquery':raise ImportError(name)
    return cq
ns={'__builtins__':{'__import__':only_import}};exec(compile(tree,'prediction','exec'),ns)
shape=ns['result'];shape=shape.val() if isinstance(shape,cq.Workplane) else shape
assert shape.isValid() and shape.Solids()
ref=cq.importers.importStep(str(target/'target.step')).val();q=evaluate(tessellate(ref),tessellate(shape));r=json.loads((target/'record.json').read_text())
shape.exportStep(str(dest/'prediction.step'));original=shape.translate(tuple(-np.array(r['translation']))).scale(1/r['scale']);original.exportStep(str(dest/'prediction_original_coordinates.step'))
solid_match=len(shape.Solids())==r['solids'];ok=solid_match and q['p95_distance_pct_diagonal']<=.5 and q['sampled_max_distance_pct_diagonal']<=2 and q['volume_error_pct']<=5
(dest/'metrics.json').write_text(json.dumps({'valid':True,'solids':len(shape.Solids()),'expected_solids':r['solids'],'solid_count_match':solid_match,'quality_vs_target':q,'geometry_pass':ok},indent=2))
