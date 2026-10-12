import cadquery as cq
import cadquery as cq
w0=cq.Workplane('ZX',origin=(0,-33,0))
w1=cq.Workplane('YZ',origin=(4,0,0))
r=w0.sketch().arc((-100,-8),(-49,-41),(-100,-70)).close().assemble().reset().face(w0.sketch().arc((-76,49),(-24,15),(-20,-45)).arc((-16,-48),(-13,-51)).segment((-13,-71)).segment((-20,-71)).arc((-22,-83),(-25,-96)).segment((94,-96)).segment((94,-83)).segment((100,-83)).segment((100,96)).segment((-100,96)).close().assemble()).push([(19,0)]).circle(65,mode='s').finalize().extrude(66).union(w1.sketch().push([(0,-24)]).circle(14).push([(0,-24.5)]).rect(12,7,mode='s').finalize().extrude(-63))
compound=r.val()
cq.exporters.export(compound, '/data/home/cuiyuehan/project/mesh2cad/ours3/cad_recode_val1000_inference_v1/step/deepcad__0056_00569330.step')
