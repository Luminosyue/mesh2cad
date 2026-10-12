import cadquery as cq
import cadquery as cq
w0=cq.Workplane('YZ',origin=(67,0,0))
w1=cq.Workplane('ZX',origin=(0,-67,0))
r=w0.sketch().segment((-60,-30),(-44,-30)).segment((-44,-22)).arc((-52,-25),(-60,-22)).close().assemble().reset().face(w0.sketch().arc((-60,22),(-52,25),(-44,22)).segment((-44,30)).segment((-60,30)).close().assemble()).reset().face(w0.sketch().segment((-32,-16),(-22,-11)).arc((-11,-5),(1,-5)).segment((32,16)).arc((28,17),(25,17)).segment((25,23)).segment((19,23)).segment((19,17)).arc((11,10),(10,-1)).segment((-10,-5)).arc((-17,-9),(-25,-7)).close().assemble()).finalize().extrude(-134).union(w0.sketch().segment((-67,-67),(67,-67)).segment((67,67)).segment((-31,67)).arc((-25,58),(-22,47)).arc((64,-1),(-31,-1)).arc((-50,-26),(-67,-53)).close().assemble().finalize().extrude(33)).union(w1.sketch().segment((-67,-100),(18,-100)).arc((-17,-72),(-22,-27)).arc((-49,-29),(-67,-10)).close().assemble().finalize().extrude(134))
compound=r.val()
cq.exporters.export(compound, '/data/home/cuiyuehan/project/mesh2cad/ours3/cad_recode_val1000_inference_v1/step/deepcad__0032_00323526.step')
