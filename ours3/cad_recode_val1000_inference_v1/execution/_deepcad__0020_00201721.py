import cadquery as cq
import cadquery as cq
w0=cq.Workplane('YZ',origin=(47,0,0))
r=w0.sketch().segment((-63,-100),(-35,-100)).segment((-35,-39)).segment((35,-39)).segment((35,-100)).segment((63,-100)).segment((63,86)).segment((35,86)).segment((35,35)).segment((-35,35)).segment((-35,86)).segment((-63,86)).close().assemble().reset().face(w0.sketch().segment((-63,-100),(-54,-100)).arc((-53,-97),(-52,-100)).segment((48,-100)).segment((48,100)).segment((-63,100)).close().assemble()).finalize().extrude(-94).union(w0.sketch().segment((-63,-59),(-16,-59)).arc((0,-61),(16,-59)).segment((63,-59)).segment((63,59)).segment((16,59)).arc((0,61),(-16,59)).segment((-63,59)).close().assemble().finalize().extrude(-59))
compound=r.val()
cq.exporters.export(compound, '/data/home/cuiyuehan/project/mesh2cad/ours3/cad_recode_val1000_inference_v1/step/deepcad__0020_00201721.step')
