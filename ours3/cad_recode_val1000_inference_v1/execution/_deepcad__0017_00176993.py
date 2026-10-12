import cadquery as cq
import cadquery as cq
w0=cq.Workplane('ZX',origin=(0,-50,0))
r=w0.sketch().segment((-50,-100),(50,-100)).segment((50,100)).segment((-50,100)).segment((-50,41)).segment((-46,41)).segment((-46,25)).segment((-50,25)).close().assemble().push([(0,-19)]).circle(40,mode='s').reset().face(w0.sketch().segment((-50,50),(-46,50)).segment((-46,52)).segment((-48,52)).segment((-48,54)).segment((-46,54)).segment((-46,56)).segment((-50,56)).close().assemble(),mode='s').reset().face(w0.sketch().segment((-25,83),(-23,83)).segment((-23,82)).segment((-18,82)).segment((-18,83)).segment((-16,83)).segment((-16,94)).segment((-18,94)).segment((-18,95)).segment((-23,95)).segment((-23,94)).segment((-25,94)).close().assemble(),mode='s').finalize().extrude(100).union(w0.sketch().arc((-50,-98),(12,0),(-50,98)).close().assemble().finalize().extrude(100))
compound=r.val()
cq.exporters.export(compound, '/data/home/cuiyuehan/project/mesh2cad/ours3/cad_recode_val1000_inference_v1/step/deepcad__0017_00176993.step')
