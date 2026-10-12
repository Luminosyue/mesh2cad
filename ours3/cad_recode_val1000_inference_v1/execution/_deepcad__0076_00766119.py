import cadquery as cq
import cadquery as cq
w0=cq.Workplane('ZX',origin=(0,-48,0))
r=w0.sketch().segment((-50,-100),(50,-100)).segment((50,100)).segment((-50,100)).segment((-50,40)).segment((-46,40)).segment((-46,25)).segment((-50,25)).close().assemble().reset().face(w0.sketch().segment((-46,25),(-45,25)).segment((-45,24)).segment((-43,24)).segment((-43,25)).segment((-42,25)).segment((-42,27)).segment((-43,27)).segment((-43,28)).segment((-45,28)).segment((-45,27)).segment((-46,27)).close().assemble(),mode='s').push([(26,-64)]).circle(13,mode='s').push([(26,43)]).circle(16,mode='s').finalize().extrude(96).union(w0.sketch().arc((-50,-98),(12,0),(-50,98)).close().assemble().finalize().extrude(96))
compound=r.val()
cq.exporters.export(compound, '/data/home/cuiyuehan/project/mesh2cad/ours3/cad_recode_val1000_inference_v1/step/deepcad__0076_00766119.step')
