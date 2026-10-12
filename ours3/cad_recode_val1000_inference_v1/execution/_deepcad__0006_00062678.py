import cadquery as cq
import cadquery as cq
w0=cq.Workplane('ZX',origin=(0,17,0))
r=w0.sketch().segment((-60,-97),(-58,-97)).segment((-58,-100)).segment((58,-100)).segment((58,-97)).segment((60,-97)).segment((60,-30)).segment((56,-30)).segment((56,-96)).segment((-58,-96)).segment((-58,-30)).segment((-60,-30)).close().assemble().reset().face(w0.sketch().segment((-60,-34),(-58,-34)).segment((-58,86)).segment((-60,86)).segment((-60,73)).arc((-59,72),(-60,71)).close().assemble()).reset().face(w0.sketch().segment((-58,96),(58,96)).segment((58,95)).arc((59,94),(59,93)).segment((60,93)).segment((60,100)).segment((-58,100)).close().assemble()).reset().face(w0.sketch().segment((56,-69),(60,-69)).segment((60,-30)).segment((58,-30)).segment((58,-34)).segment((56,-34)).close().assemble()).finalize().extrude(-34).union(w0.sketch().arc((56,-68),(60,-44),(56,-19)).close().assemble().finalize().extrude(-34)).union(w0.workplane(offset=-24/2).moveTo(-59,0).box(2,80,24))
compound=r.val()
cq.exporters.export(compound, '/data/home/cuiyuehan/project/mesh2cad/ours3/cad_recode_val1000_inference_v1/step/deepcad__0006_00062678.step')
