import cadquery as cq
import cadquery as cq
w0=cq.Workplane('ZX',origin=(0,-100,0))
w1=cq.Workplane('ZX',origin=(0,-87,0))
r=w0.workplane(offset=45/2).cylinder(45,28).union(w0.workplane(offset=200/2).cylinder(200,28)).union(w1.sketch().arc((-6,-27),(0,-28),(6,-27)).close().assemble().reset().face(w1.sketch().segment((-6,27),(6,27)).arc((0,28),(-6,27)).assemble()).reset().face(w1.sketch().arc((11,-25),(21,0),(11,25)).close().assemble()).finalize().extrude(110))
compound=r.val()
cq.exporters.export(compound, '/data/home/cuiyuehan/project/mesh2cad/ours3/cad_recode_val1000_inference_v1/step/deepcad__0035_00357667.step')
