import cadquery as cq
import cadquery as cq
w0=cq.Workplane('XY',origin=(0,0,42))
r=w0.sketch().segment((-71,-100),(34,-100)).segment((34,-94)).segment((71,-37)).segment((71,-10)).segment((34,-67)).segment((34,-49)).arc((27,-23),(51,-7)).segment((28,22)).arc((-18,-30),(-60,29)).segment((-71,29)).close().assemble().reset().face(w0.sketch().segment((-71,57),(-60,57)).arc((-18,79),(28,57)).segment((59,57)).segment((59,100)).segment((-71,100)).close().assemble()).reset().face(w0.sketch().segment((-36,34),(-28,20)).arc((-1,35),(28,25)).segment((19,40)).arc((1,36),(-17,41)).close().assemble()).finalize().extrude(-84).union(w0.sketch().segment((-71,-100),(26,-100)).segment((26,-72)).segment((57,-72)).segment((57,-62)).arc((30,-18),(71,12)).segment((71,97)).segment((46,97)).segment((46,29)).segment((26,29)).segment((26,37)).segment((-71,37)).close().assemble().finalize().extrude(-18))
compound=r.val()
cq.exporters.export(compound, '/data/home/cuiyuehan/project/mesh2cad/ours3/cad_recode_val1000_inference_v1/step/deepcad__0078_00789912.step')
