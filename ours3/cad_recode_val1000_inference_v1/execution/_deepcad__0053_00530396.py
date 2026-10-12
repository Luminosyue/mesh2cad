import cadquery as cq
import cadquery as cq
w0=cq.Workplane('ZX',origin=(0,-45,0))
r=w0.sketch().segment((-78,-100),(78,-100)).segment((78,-56)).segment((-33,-56)).segment((-33,45)).segment((-78,63)).close().assemble().reset().face(w0.sketch().segment((-78,70),(-33,52)).segment((-33,90)).segment((-78,100)).close().assemble()).finalize().extrude(71).union(w0.sketch().segment((-78,-90),(-33,-90)).segment((-33,-81)).segment((-78,-52)).close().assemble().reset().face(w0.sketch().segment((-78,-42),(-33,-71)).segment((-33,90)).segment((-78,90)).close().assemble()).reset().face(w0.sketch().segment((11,-56),(59,-84)).segment((68,-69)).segment((68,-56)).close().assemble()).finalize().extrude(90))
compound=r.val()
cq.exporters.export(compound, '/data/home/cuiyuehan/project/mesh2cad/ours3/cad_recode_val1000_inference_v1/step/deepcad__0053_00530396.step')
