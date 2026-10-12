import cadquery as cq
import cadquery as cq
w0=cq.Workplane('XY',origin=(0,0,-16))
w1=cq.Workplane('XY',origin=(0,0,-8))
r=w0.sketch().segment((-61,15),(-60,-38)).segment((-14,-38)).segment((-14,-37)).arc((-19,-1),(-46,24)).segment((-46,15)).close().assemble().reset().face(w0.sketch().segment((-22,58),(4,33)).segment((12,52)).arc((0,70),(4,92)).segment((-7,97)).close().assemble()).reset().face(w0.sketch().arc((10,-38),(14,-40),(18,-41)).segment((18,-38)).close().assemble()).reset().face(w0.sketch().segment((23,-100),(23,-51)).arc((12,-76),(23,-100)).assemble()).reset().face(w0.sketch().arc((23,-10),(45,-24),(70,-18)).segment((23,27)).arc((24,23),(25,20)).arc((33,17),(32,9)).arc((28,15),(23,20)).close().assemble()).finalize().extrude(32).union(w0.sketch().segment((-70,54),(-59,21)).arc((-61,1),(-47,-15)).segment((-36,-48)).segment((-7,-39)).segment((-18,-5)).arc((-16,15),(-30,30)).segment((-41,63)).close().assemble().finalize().extrude(32)).union(w1.sketch().arc((-74,75),(-65,63),(-67,48)).arc((-60,64),(-74,75)).assemble().finalize().extrude(10))
compound=r.val()
cq.exporters.export(compound, '/data/home/cuiyuehan/project/mesh2cad/ours3/cad_recode_val1000_inference_v1/step/deepcad__0022_00220997.step')
