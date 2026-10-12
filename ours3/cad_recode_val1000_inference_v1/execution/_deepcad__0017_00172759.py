import cadquery as cq
import cadquery as cq
w0=cq.Workplane('YZ',origin=(-94,0,0))
w1=cq.Workplane('YZ',origin=(-100,0,0))
r=w0.sketch().segment((-9,-9),(9,-9)).segment((9,9)).segment((-9,9)).segment((-9,-1)).segment((-8,-1)).segment((-8,-3)).segment((-9,-3)).close().assemble().rect(8,8,mode='s').finalize().extrude(182).union(w1.sketch().rect(18,8).rect(8,8,mode='s').finalize().extrude(200))
compound=r.val()
cq.exporters.export(compound, '/data/home/cuiyuehan/project/mesh2cad/ours3/cad_recode_val1000_inference_v1/step/deepcad__0017_00172759.step')
