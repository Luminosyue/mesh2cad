import cadquery as cq
import cadquery as cq
w0=cq.Workplane('ZX',origin=(0,-2,0))
r=w0.sketch().segment((-24,-98),(-19,-100)).segment((-12,-77)).arc((-1,-79),(1,-68)).segment((24,-58)).segment((12,-26)).arc((12,-9),(4,7)).segment((23,54)).segment((14,58)).segment((14,66)).segment((10,66)).segment((10,59)).segment((-1,63)).segment((-3,63)).segment((-3,73)).segment((-1,81)).segment((-24,100)).segment((-24,22)).arc((-25,0),(-20,-22)).segment((-24,-22)).segment((-24,-37)).arc((-23,-38),(-24,-39)).close().assemble().reset().face(w0.sketch().segment((-24,-22),(-19,-22)).segment((-24,-18)).close().assemble(),mode='s').reset().face(w0.sketch().segment((-16,-46),(-10,-50)).segment((-10,-46)).close().assemble(),mode='s').reset().face(w0.sketch().segment((-3,-75),(3,-73)).segment((-3,-60)).close().assemble(),mode='s').finalize().extrude(4)
compound=r.val()
cq.exporters.export(compound, '/data/home/cuiyuehan/project/mesh2cad/ours3/cad_recode_val1000_inference_v1/step/deepcad__0018_00183099.step')
