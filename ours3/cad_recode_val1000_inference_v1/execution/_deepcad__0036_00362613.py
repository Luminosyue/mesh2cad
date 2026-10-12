import cadquery as cq
import cadquery as cq
w0=cq.Workplane('XY',origin=(0,0,-80))
w1=cq.Workplane('XY',origin=(0,0,-4))
r=w0.sketch().segment((-32,-95),(32,-95)).segment((32,-71)).arc((81,0),(32,71)).segment((32,95)).segment((-32,95)).segment((-32,71)).arc((-81,0),(-32,-71)).close().assemble().finalize().extrude(19).union(w0.sketch().segment((-91,41),(-91,42)).arc((-99,-13),(-78,-63)).arc((-60,-64),(-52,-82)).arc((-43,-87),(-32,-95)).arc((1,-100),(33,-95)).arc((14,-85),(-1,-70)).arc((100,0),(-1,70)).arc((36,24),(28,-38)).arc((-35,35),(-91,41)).assemble().finalize().extrude(160)).union(w1.workplane(offset=10/2).cylinder(10,100))
compound=r.val()
cq.exporters.export(compound, '/data/home/cuiyuehan/project/mesh2cad/ours3/cad_recode_val1000_inference_v1/step/deepcad__0036_00362613.step')
