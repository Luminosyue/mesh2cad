import cadquery as cq
import cadquery as cq
w0=cq.Workplane('ZX',origin=(0,-100,0))
w1=cq.Workplane('ZX',origin=(0,-87,0))
r=w0.sketch().arc((-50,2),(-48,-14),(-42,-29)).close().assemble().reset().face(w0.sketch().segment((-49,8),(-23,27)).segment((-49,27)).close().assemble()).reset().face(w0.sketch().arc((-40,-30),(1,-50),(42,-29)).close().assemble()).reset().face(w0.sketch().segment((-40,29),(42,29)).arc((1,50),(-40,29)).assemble()).reset().face(w0.sketch().arc((47,-17),(50,0),(47,17)).close().assemble()).finalize().extrude(114).union(w1.sketch().arc((-22,-13),(-18,-10),(-15,-13)).arc((-1,-49),(34,-36)).arc((43,-25),(49,-10)).arc((-14,48),(-22,-13)).assemble().finalize().extrude(187))
compound=r.val()
cq.exporters.export(compound, '/data/home/cuiyuehan/project/mesh2cad/ours3/cad_recode_val1000_inference_v1/step/deepcad__0044_00442258.step')
