import cadquery as cq
import cadquery as cq
w0=cq.Workplane('XY',origin=(0,0,100))
w1=cq.Workplane('XY',origin=(0,0,58))
r=w0.sketch().arc((-2,-2),(0,-3),(2,-2)).close().assemble().reset().face(w0.sketch().segment((-2,2),(2,2)).arc((0,3),(-2,2)).assemble()).finalize().extrude(-195).union(w1.workplane(offset=-158/2).cylinder(158,3))
compound=r.val()
cq.exporters.export(compound, '/data/home/cuiyuehan/project/mesh2cad/ours3/cad_recode_val1000_inference_v1/step/deepcad__0083_00835011.step')
