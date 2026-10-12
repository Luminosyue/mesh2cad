import sys,json
from pathlib import Path
sys.path.insert(0,str(Path(__file__).parents[1]))
import numpy as np
from OCP.BRepCheck import BRepCheck_Analyzer
from OCP.BRepBuilderAPI import BRepBuilderAPI_MakeFace
from builders.bspline_skin_builder import surface
from builders.common import profile_points
spec=json.load(open('/data/home/cuiyuehan/project/mesh2cad/ours3/v7_contract_closed_runtime/04_measured_spec/CADPART_005/measured_cad_spec.json'))
g=np.asarray([profile_points(spec,p) for p in spec['profiles']]);h=g.shape[1]//2
for name,grid in [('upper',g[:,:h+1]),('lower',np.concatenate([g[:,h:],g[:,:1]],axis=1))]:
 s=surface(grid,.0005);f=BRepBuilderAPI_MakeFace(s,1e-6).Face();print(name,'face',BRepCheck_Analyzer(f).IsValid(),'bounds',s.Bounds())
