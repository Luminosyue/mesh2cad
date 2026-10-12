import cadquery as cq
import cadquery as cq
w0=cq.Workplane('ZX',origin=(0,-28,0))
r=w0.sketch().segment((-65,-88),(46,-88)).segment((46,-39)).segment((65,-39)).segment((65,19)).segment((46,19)).segment((46,62)).segment((-65,62)).close().assemble().push([(0,-13)]).circle(20,mode='s').finalize().extrude(1).union(w0.sketch().segment((-65,-100),(65,-100)).segment((65,-29)).segment((63,-29)).segment((63,-16)).segment((65,-16)).segment((65,100)).segment((-65,100)).close().assemble().reset().face(w0.sketch().segment((-63,-58),(-18,-58)).arc((-24,-43),(-24,-27)).segment((-63,-27)).close().assemble(),mode='s').reset().face(w0.sketch().segment((-63,27),(-24,27)).arc((-24,33),(-22,39)).segment((-63,39)).close().assemble(),mode='s').finalize().extrude(57))
compound=r.val()
cq.exporters.export(compound, '/data/home/cuiyuehan/project/mesh2cad/ours3/cad_recode_val1000_inference_v1/step/deepcad__0062_00625397.step')
