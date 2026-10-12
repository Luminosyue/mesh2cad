import cadquery as cq
import cadquery as cq
w0=cq.Workplane('ZX',origin=(0,-43,0))
r=w0.sketch().segment((-60,-56),(-47,-56)).segment((-47,-100)).segment((25,-100)).segment((25,-83)).segment((-34,-83)).segment((-34,-39)).segment((25,-39)).segment((25,-14)).segment((60,-14)).segment((60,100)).segment((-60,100)).close().assemble().reset().face(w0.sketch().segment((-60,-10),(-59,-12)).segment((-56,-11)).segment((-57,-8)).close().assemble(),mode='s').reset().face(w0.sketch().segment((25,-11),(34,-11)).segment((34,32)).segment((60,32)).segment((60,69)).segment((25,69)).close().assemble(),mode='s').finalize().extrude(86).union(w0.sketch().segment((-60,-100),(60,-100)).segment((60,62)).segment((-12,62)).arc((-35,20),(-60,59)).close().assemble().finalize().extrude(86))
compound=r.val()
cq.exporters.export(compound, '/data/home/cuiyuehan/project/mesh2cad/ours3/cad_recode_val1000_inference_v1/step/deepcad__0049_00493545.step')
