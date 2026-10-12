import cadquery as cq
import cadquery as cq
w0=cq.Workplane('ZX',origin=(0,10,0))
r=w0.sketch().segment((-45,-100),(13,-100)).segment((13,-81)).segment((19,-81)).segment((19,-75)).segment((30,-81)).segment((45,-81)).segment((45,-35)).segment((13,-35)).segment((13,-24)).segment((-45,-24)).close().assemble().reset().face(w0.sketch().segment((-45,-2),(13,10)).segment((45,10)).segment((45,57)).segment((24,82)).segment((-45,21)).close().assemble()).reset().face(w0.sketch().segment((-45,44),(-24,59)).segment((13,13)).segment((13,100)).segment((-35,100)).segment((-35,93)).segment((-45,93)).close().assemble()).finalize().extrude(-20).union(w0.sketch().segment((-23,-100),(26,-100)).arc((1,-43),(-23,-100)).assemble().finalize().extrude(-16))
compound=r.val()
cq.exporters.export(compound, '/data/home/cuiyuehan/project/mesh2cad/ours3/cad_recode_val1000_inference_v1/step/deepcad__0009_00096823.step')
