import cadquery as cq
import cadquery as cq
w0=cq.Workplane('ZX',origin=(0,-4,0))
w1=cq.Workplane('ZX',origin=(0,-14,0))
r=w0.sketch().circle(19).circle(18,mode='s').finalize().extrude(-96).union(w0.sketch().circle(18).circle(17,mode='s').finalize().extrude(98)).union(w0.sketch().arc((-19,1),(-17,-6),(-15,-12)).segment((-14,-12)).arc((-17,-5),(-19,1)).assemble().reset().face(w0.sketch().arc((4,-18),(13,-14),(19,-6)).segment((18,-6)).arc((15,-12),(9,-15)).close().assemble()).reset().face(w0.sketch().segment((18,6),(19,6)).arc((18,7),(18,8)).close().assemble()).finalize().extrude(104)).union(w1.workplane(offset=-82/2).cylinder(82,18))
compound=r.val()
cq.exporters.export(compound, '/data/home/cuiyuehan/project/mesh2cad/ours3/cad_recode_val1000_inference_v1/step/deepcad__0059_00597907.step')
