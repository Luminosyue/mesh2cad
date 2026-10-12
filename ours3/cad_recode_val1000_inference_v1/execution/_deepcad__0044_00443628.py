import cadquery as cq
import cadquery as cq
w0=cq.Workplane('XY',origin=(0,0,100))
w1=cq.Workplane('XY',origin=(0,0,15))
r=w0.sketch().arc((16,-38),(17,-36),(19,-37)).arc((1,39),(16,-38)).assemble().finalize().extrude(-188).union(w0.sketch().arc((-35,-22),(35,21),(-34,-24)).segment((-24,-24)).segment((-24,-16)).segment((-35,-16)).close().assemble().finalize().extrude(-49)).union(w1.sketch().arc((-40,-9),(-39,-13),(-37,-17)).arc((36,19),(-40,-9)).assemble().push([(1,0)]).circle(20,mode='s').finalize().extrude(-111))
compound=r.val()
cq.exporters.export(compound, '/data/home/cuiyuehan/project/mesh2cad/ours3/cad_recode_val1000_inference_v1/step/deepcad__0044_00443628.step')
