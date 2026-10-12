import cadquery as cq
import cadquery as cq
w0=cq.Workplane('ZX',origin=(0,-45,0))
r=w0.sketch().segment((-78,-100),(-45,-100)).segment((-78,-53)).close().assemble().reset().face(w0.sketch().segment((-78,-52),(78,73)).segment((78,97)).segment((60,97)).segment((60,100)).segment((-78,100)).close().assemble()).reset().face(w0.sketch().segment((-78,-15),(-78,58)).arc((-81,21),(-78,-15)).assemble()).reset().face(w0.sketch().segment((-37,-100),(78,-100)).segment((78,-24)).close().assemble()).finalize().extrude(80).union(w0.sketch().arc((-78,-73),(-15,14),(-78,91)).close().assemble().finalize().extrude(90))
compound=r.val()
cq.exporters.export(compound, '/data/home/cuiyuehan/project/mesh2cad/ours3/cad_recode_val1000_inference_v1/step/deepcad__0061_00613626.step')
