import cadquery as cq
import cadquery as cq
w0=cq.Workplane('XY',origin=(0,0,9))
w1=cq.Workplane('XY',origin=(0,0,-7))
r=w0.workplane(offset=-25/2).moveTo(-66,-25).box(6,14,25).union(w0.sketch().segment((-100,-28),(-97,-28)).segment((-97,-32)).segment((-94,-33)).segment((-94,-18)).segment((-98,-18)).close().assemble().reset().face(w0.sketch().segment((-85,-29),(-61,-33)).segment((-60,-20)).segment((-63,-20)).segment((-63,-25)).segment((-85,-25)).close().assemble()).finalize().extrude(7)).union(w1.sketch().segment((42,-10),(50,-10)).arc((52,-22),(62,-24)).arc((78,-26),(93,-21)).arc((99,-18),(98,-11)).arc((97,0),(92,11)).arc((83,23),(69,33)).arc((67,31),(65,28)).arc((51,15),(45,-3)).segment((42,-3)).close().assemble().finalize().extrude(11))
compound=r.val()
cq.exporters.export(compound, '/data/home/cuiyuehan/project/mesh2cad/ours3/cad_recode_val1000_inference_v1/step/deepcad__0072_00725796.step')
