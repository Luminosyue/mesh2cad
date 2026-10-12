import cadquery as cq
import cadquery as cq
w0=cq.Workplane('XY',origin=(0,0,100))
w1=cq.Workplane('XY',origin=(0,0,88))
r=w0.sketch().segment((-52,-12),(-42,-21)).arc((-45,11),(-28,38)).segment((-33,41)).close().assemble().reset().face(w0.sketch().segment((-25,-45),(-20,-49)).segment((-13,-45)).arc((-19,-45),(-25,-45)).assemble()).reset().face(w0.sketch().arc((11,45),(17,44),(23,42)).segment((19,46)).segment((18,45)).close().assemble()).reset().face(w0.sketch().segment((25,-40),(38,-28)).segment((36,-25)).arc((33,-34),(25,-40)).assemble()).finalize().extrude(-194).union(w0.sketch().arc((-46,25),(-47,-23),(-14,-50)).arc((-44,-17),(-46,25)).assemble().reset().face(w0.sketch().arc((-3,46),(40,25),(40,-25)).arc((41,-23),(41,-21)).arc((47,23),(13,50)).arc((6,46),(-3,46)).assemble()).finalize().extrude(-193)).union(w1.sketch().arc((-34,-38),(1,-53),(34,-38)).segment((29,-38)).arc((1,-47),(-27,-38)).close().assemble().finalize().extrude(-188))
compound=r.val()
cq.exporters.export(compound, '/data/home/cuiyuehan/project/mesh2cad/ours3/cad_recode_val1000_inference_v1/step/deepcad__0098_00988738.step')
