import cadquery as cq
import cadquery as cq
w0=cq.Workplane('XY',origin=(0,0,0))
r=w0.sketch().segment((-2,-39),(0,-39)).segment((2,1)).segment((0,1)).segment((0,0)).segment((-1,0)).segment((-1,-39)).segment((1,-39)).segment((1,0)).segment((0,0)).segment((0,1)).segment((1,1)).segment((1,39)).segment((0,39)).segment((0,1)).segment((-1,1)).segment((-1,-39)).segment((-2,-39)).close().assemble().reset().face(w0.sketch().segment((-1,-100),(2,-95)).segment((0,-95)).segment((0,-94)).segment((2,-94)).segment((1,-92)).segment((0,-92)).segment((0,-90)).close().assemble()).finalize().extrude(-1)
compound=r.val()
cq.exporters.export(compound, '/data/home/cuiyuehan/project/mesh2cad/ours3/cad_recode_val1000_inference_v1/step/deepcad__0080_00806503.step')
