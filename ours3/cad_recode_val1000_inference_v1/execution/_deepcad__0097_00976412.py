import cadquery as cq
import cadquery as cq
w0=cq.Workplane('ZX',origin=(0,-31,0))
r=w0.sketch().segment((-56,-68),(-27,-68)).segment((-27,-90)).segment((18,-90)).segment((18,-68)).segment((56,-68)).segment((56,-24)).arc((15,-1),(56,22)).segment((56,93)).segment((18,93)).segment((18,94)).segment((-27,94)).segment((-27,93)).segment((-56,93)).close().assemble().finalize().extrude(1).union(w0.sketch().segment((-56,-100),(56,-100)).segment((56,-6)).arc((53,-12),(50,-17)).segment((50,-24)).segment((43,-24)).arc((0,-61),(-43,-24)).segment((-50,-24)).segment((-50,-17)).arc((-53,-12),(-56,-6)).close().assemble().reset().face(w0.sketch().arc((-56,24),(-53,29),(-50,34)).segment((-50,41)).segment((-43,41)).arc((0,77),(50,41)).segment((56,41)).segment((56,100)).segment((-56,100)).close().assemble()).finalize().extrude(62))
compound=r.val()
cq.exporters.export(compound, '/data/home/cuiyuehan/project/mesh2cad/ours3/cad_recode_val1000_inference_v1/step/deepcad__0097_00976412.step')
