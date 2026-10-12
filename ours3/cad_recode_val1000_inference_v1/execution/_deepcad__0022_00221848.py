import cadquery as cq
import cadquery as cq
w0=cq.Workplane('ZX',origin=(0,-100,0))
w1=cq.Workplane('ZX',origin=(0,-66,0))
r=w0.sketch().arc((-30,-29),(1,15),(32,-25)).arc((-1,42),(-30,-29)).assemble().finalize().extrude(9).union(w0.sketch().arc((-39,12),(-40,-8),(-31,-27)).arc((-16,-3),(10,13)).arc((-1,16),(-11,16)).arc((-15,24),(-15,33)).segment((-19,37)).arc((-27,30),(-36,20)).arc((-37,16),(-39,12)).assemble().finalize().extrude(199)).union(w1.sketch().arc((-19,-37),(10,-40),(34,-23)).arc((31,-24),(28,-24)).arc((1,-36),(-1,-7)).arc((-16,16),(7,32)).arc((17,34),(27,31)).arc((28,31),(30,30)).arc((25,33),(20,35)).arc((14,39),(7,40)).arc((11,38),(14,35)).arc((13,34),(12,32)).arc((-14,8),(-19,-26)).arc((-18,-31),(-19,-37)).assemble().finalize().extrude(148))
compound=r.val()
cq.exporters.export(compound, '/data/home/cuiyuehan/project/mesh2cad/ours3/cad_recode_val1000_inference_v1/step/deepcad__0022_00221848.step')
