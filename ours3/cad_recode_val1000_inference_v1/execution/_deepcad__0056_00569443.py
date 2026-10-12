import cadquery as cq
import cadquery as cq
w0=cq.Workplane('ZX',origin=(0,-9,0))
w1=cq.Workplane('YZ',origin=(66,0,0))
r=w0.sketch().push([(-59,-83)]).rect(34,34).reset().face(w0.sketch().segment((23,-2),(24,-6)).arc((23,-13),(28,-18)).segment((29,-24)).segment((36,-25)).segment((35,-21)).arc((37,-19),(38,-16)).segment((56,-12)).segment((53,2)).close().assemble()).finalize().extrude(-33).union(w0.workplane(offset=-16/2).moveTo(45,-3).cylinder(16,12)).union(w1.sketch().segment((8,-59),(42,-59)).segment((42,-10)).segment((43,-10)).segment((43,-1)).segment((42,-1)).segment((42,76)).segment((8,76)).segment((8,-1)).segment((8,-10)).close().assemble().finalize().extrude(34))
compound=r.val()
cq.exporters.export(compound, '/data/home/cuiyuehan/project/mesh2cad/ours3/cad_recode_val1000_inference_v1/step/deepcad__0056_00569443.step')
