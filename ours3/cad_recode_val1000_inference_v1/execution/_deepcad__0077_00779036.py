import cadquery as cq
import cadquery as cq
w0=cq.Workplane('XY',origin=(0,0,-2))
r=w0.sketch().segment((-100,4),(-93,4)).segment((-93,-4)).segment((-52,-4)).arc((-58,0),(-64,4)).segment((-93,4)).segment((-93,3)).segment((-97,3)).segment((-97,4)).close().assemble().reset().face(w0.sketch().segment((-45,-4),(100,-4)).segment((100,4)).segment((-42,4)).arc((-42,0),(-45,-4)).assemble()).reset().face(w0.sketch().segment((20,-1),(21,-3)).segment((24,-1)).segment((23,1)).close().assemble(),mode='s').finalize().extrude(4)
compound=r.val()
cq.exporters.export(compound, '/data/home/cuiyuehan/project/mesh2cad/ours3/cad_recode_val1000_inference_v1/step/deepcad__0077_00779036.step')
