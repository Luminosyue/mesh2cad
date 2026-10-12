import cadquery as cq
import cadquery as cq
w0=cq.Workplane('ZX',origin=(0,-79,0))
r=w0.sketch().segment((-78,-100),(78,-100)).segment((78,100)).segment((-78,100)).segment((-78,71)).segment((-78,-69)).close().assemble().reset().face(w0.sketch().segment((-78,-60),(-78,51)).arc((-87,-4),(-78,-60)).assemble(),mode='s').reset().face(w0.sketch().arc((-56,-100),(0,-99),(56,-100)).segment((-11,-100)).close().assemble()).reset().face(w0.sketch().segment((-56,100),(56,100)).arc((0,99),(-56,100)).assemble()).reset().face(w0.sketch().arc((78,-60),(87,-4),(78,51)).close().assemble(),mode='s').finalize().extrude(158)
compound=r.val()
cq.exporters.export(compound, '/data/home/cuiyuehan/project/mesh2cad/ours3/cad_recode_val1000_inference_v1/step/deepcad__0094_00945780.step')
