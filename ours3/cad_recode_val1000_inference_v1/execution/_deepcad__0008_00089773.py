import cadquery as cq
import cadquery as cq
w0=cq.Workplane('ZX',origin=(0,-100,0))
w1=cq.Workplane('ZX',origin=(0,-43,0))
r=w0.sketch().arc((-65,-24),(-58,-37),(-48,-49)).segment((-48,-34)).close().assemble().reset().face(w0.sketch().arc((-53,44),(-44,48),(-34,51)).segment((-53,45)).close().assemble()).reset().face(w0.sketch().arc((-15,-67),(35,-59),(67,-18)).close().assemble()).reset().face(w0.sketch().segment((11,68),(67,-15)).arc((58,36),(11,68)).assemble()).finalize().extrude(191).union(w0.sketch().arc((-70,0),(-68,-9),(-67,-18)).arc((-49,-49),(-20,-66)).arc((-33,-49),(-39,-29)).arc((-43,13),(-10,43)).arc((1,45),(12,43)).arc((27,36),(40,25)).arc((55,18),(69,7)).arc((1,69),(-70,0)).assemble().finalize().extrude(200)).union(w1.sketch().arc((-26,-36),(1,-45),(28,-36)).close().assemble().finalize().extrude(88))
compound=r.val()
cq.exporters.export(compound, '/data/home/cuiyuehan/project/mesh2cad/ours3/cad_recode_val1000_inference_v1/step/deepcad__0008_00089773.step')
