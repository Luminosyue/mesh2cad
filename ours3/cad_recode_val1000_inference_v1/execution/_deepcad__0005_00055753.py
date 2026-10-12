import cadquery as cq
import cadquery as cq
w0=cq.Workplane('XY',origin=(0,0,9))
w1=cq.Workplane('ZX',origin=(0,18,0))
r=w0.sketch().segment((-60,-96),(-49,-96)).segment((-49,-97)).segment((-34,-97)).segment((-34,-96)).segment((-23,-96)).segment((-23,-95)).segment((-17,-95)).segment((-17,-78)).segment((-11,-78)).segment((-11,-100)).segment((37,-100)).segment((37,-96)).segment((60,-96)).segment((60,-68)).segment((55,-68)).segment((55,-74)).segment((40,-74)).segment((40,-68)).segment((28,-68)).segment((28,-27)).segment((40,-27)).segment((40,-21)).segment((55,-21)).segment((55,-27)).segment((60,-27)).segment((60,85)).segment((50,85)).segment((50,100)).segment((-34,100)).segment((-34,100)).segment((-49,100)).segment((-49,95)).segment((-60,95)).segment((-60,68)).arc((-54,70),(-49,72)).segment((-49,87)).segment((-40,87)).segment((-40,59)).arc((-10,-10),(-53,50)).arc((-56,46),(-60,43)).close().assemble().finalize().extrude(12).union(w1.sketch().arc((-21,-44),(21,0),(-21,44)).segment((-21,25)).arc((-11,0),(-21,-25)).close().assemble().finalize().extrude(-12))
compound=r.val()
cq.exporters.export(compound, '/data/home/cuiyuehan/project/mesh2cad/ours3/cad_recode_val1000_inference_v1/step/deepcad__0005_00055753.step')
