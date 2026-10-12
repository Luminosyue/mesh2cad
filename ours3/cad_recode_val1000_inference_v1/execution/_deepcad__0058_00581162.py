import cadquery as cq
import cadquery as cq
w0=cq.Workplane('ZX',origin=(0,-62,0))
r=w0.sketch().segment((-75,-100),(75,-100)).segment((75,97)).arc((34,81),(11,100)).segment((-75,100)).close().assemble().reset().face(w0.sketch().segment((-75,-68),(-69,-68)).arc((-73,-57),(-75,-46)).close().assemble(),mode='s').reset().face(w0.sketch().arc((-75,-35),(-73,-24),(-69,-13)).segment((-75,-13)).close().assemble(),mode='s').reset().face(w0.sketch().segment((-15,-68),(22,-68)).segment((22,-13)).segment((-15,-13)).arc((-11,-41),(-15,-68)).assemble(),mode='s').finalize().extrude(120).union(w0.sketch().segment((-75,-100),(75,-100)).segment((75,100)).segment((-75,100)).segment((-75,13)).segment((-47,13)).segment((-47,-13)).segment((-75,-13)).close().assemble().push([(14,-34)]).circle(23,mode='s').finalize().extrude(125))
compound=r.val()
cq.exporters.export(compound, '/data/home/cuiyuehan/project/mesh2cad/ours3/cad_recode_val1000_inference_v1/step/deepcad__0058_00581162.step')
