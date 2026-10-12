import cadquery as cq
import cadquery as cq
w0=cq.Workplane('ZX',origin=(0,-27,0))
r=w0.sketch().segment((-40,-100),(-23,-100)).segment((-23,-88)).segment((40,-88)).segment((40,96)).segment((31,96)).segment((31,100)).segment((-40,100)).close().assemble().reset().face(w0.sketch().segment((-40,83),(-39,83)).segment((-39,82)).segment((-36,82)).segment((-36,83)).segment((-35,83)).segment((-35,92)).segment((-36,92)).segment((-36,93)).segment((-39,93)).segment((-39,92)).segment((-40,92)).close().assemble(),mode='s').reset().face(w0.sketch().segment((-39,-29),(-36,-29)).segment((-36,-28)).segment((-39,-28)).close().assemble(),mode='s').reset().face(w0.sketch().segment((-23,-29),(-20,-29)).segment((-20,-28)).segment((-23,-28)).arc((-22,-30),(-23,-29)).assemble(),mode='s').push([(18,35)]).circle(5,mode='s').finalize().extrude(54)
compound=r.val()
cq.exporters.export(compound, '/data/home/cuiyuehan/project/mesh2cad/ours3/cad_recode_val1000_inference_v1/step/deepcad__0039_00398168.step')
