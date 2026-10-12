import cadquery as cq
import cadquery as cq
w0=cq.Workplane('XY',origin=(0,0,4))
r=w0.sketch().segment((-100,-9),(-68,-9)).segment((-53,-2)).segment((-50,-9)).segment((-3,-9)).segment((-3,9)).segment((-100,9)).close().assemble().reset().face(w0.sketch().segment((11,-9),(100,-9)).segment((100,9)).segment((11,9)).segment((11,7)).arc((16,0),(11,-7)).close().assemble()).finalize().extrude(-8)
compound=r.val()
cq.exporters.export(compound, '/data/home/cuiyuehan/project/mesh2cad/ours3/cad_recode_val1000_inference_v1/step/deepcad__0056_00569684.step')
