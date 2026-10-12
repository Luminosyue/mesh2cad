import cadquery as cq
import cadquery as cq
w0=cq.Workplane('ZX',origin=(0,-53,0))
w1=cq.Workplane('ZX',origin=(0,-20,0))
r=w0.sketch().arc((-92,1),(-88,-10),(-80,-19)).arc((-78,-59),(-46,-86)).segment((-32,-94)).segment((-28,-88)).arc((24,-86),(66,-52)).arc((31,-34),(45,5)).arc((42,17),(37,26)).arc((35,30),(33,34)).arc((32,33),(31,33)).arc((17,42),(1,45)).arc((-13,49),(-27,49)).arc((-52,41),(-74,27)).arc((-77,26),(-81,24)).segment((-69,1)).arc((-70,-1),(-71,-3)).close().assemble().finalize().extrude(2).union(w0.sketch().arc((-90,42),(-88,-44),(-13,-97)).segment((-13,-100)).segment((10,-99)).close().assemble().reset().face(w0.sketch().segment((-74,66),(62,76)).arc((5,99),(-56,81)).arc((-65,75),(-74,66)).assemble()).reset().face(w0.sketch().arc((49,-85),(73,-68),(85,-43)).close().assemble()).reset().face(w0.sketch().segment((77,43),(99,-7)).arc((95,24),(77,43)).assemble()).finalize().extrude(106)).union(w1.workplane(offset=42/2).moveTo(0,11).cylinder(42,34))
compound=r.val()
cq.exporters.export(compound, '/data/home/cuiyuehan/project/mesh2cad/ours3/cad_recode_val1000_inference_v1/step/deepcad__0087_00875795.step')
