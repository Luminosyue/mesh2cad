import cadquery as cq
import cadquery as cq
w0=cq.Workplane('ZX',origin=(0,60,0))
w1=cq.Workplane('XY',origin=(0,0,-20))
r=w0.sketch().segment((-60,-72),(-20,-72)).segment((-20,-60)).segment((17,-60)).arc((-34,-18),(17,24)).segment((-20,24)).segment((-20,60)).segment((-60,60)).segment((-60,38)).arc((-59,37),(-60,36)).close().assemble().reset().face(w0.sketch().segment((-60,-100),(-20,-100)).segment((-20,-60)).segment((17,-60)).arc((16,-59),(16,-58)).arc((-27,-52),(-60,-23)).close().assemble()).reset().face(w0.sketch().arc((-60,36),(-59,37),(-59,38)).segment((-60,38)).close().assemble()).reset().face(w0.sketch().arc((-19,60),(20,51),(56,24)).segment((60,24)).segment((60,60)).close().assemble()).reset().face(w0.sketch().segment((29,-24),(60,-24)).segment((60,-58)).arc((59,-41),(53,-24)).close().assemble()).finalize().extrude(-120).union(w1.sketch().segment((-100,-60),(100,-60)).segment((100,60)).segment((87,60)).arc((23,-10),(-51,60)).segment((-100,60)).close().assemble().finalize().extrude(-40))
compound=r.val()
cq.exporters.export(compound, '/data/home/cuiyuehan/project/mesh2cad/ours3/cad_recode_val1000_inference_v1/step/deepcad__0025_00255754.step')
