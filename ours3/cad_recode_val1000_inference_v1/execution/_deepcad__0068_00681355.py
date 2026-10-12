import cadquery as cq
import cadquery as cq
w0=cq.Workplane('XY',origin=(0,0,100))
w1=cq.Workplane('ZX',origin=(0,-33,0))
r=w0.sketch().segment((-40,17),(-19,31)).arc((-31,26),(-40,17)).assemble().reset().face(w0.sketch().segment((-13,11),(53,11)).arc((51,14),(50,17)).close().assemble()).reset().face(w0.sketch().arc((-7,33),(1,31),(9,27)).segment((13,32)).arc((0,33),(-7,33)).assemble()).reset().face(w0.sketch().arc((12,11),(23,9),(33,4)).segment((53,13)).arc((33,26),(12,32)).close().assemble()).reset().face(w0.sketch().arc((19,11),(23,9),(28,7)).close().assemble()).reset().face(w0.sketch().arc((67,-20),(67,-22),(68,-23)).segment((77,-34)).arc((73,-22),(67,-10)).close().assemble()).finalize().extrude(-200).union(w0.sketch().arc((-76,-33),(-65,-34),(-55,-33)).close().assemble().finalize().extrude(-199)).union(w1.sketch().arc((-99,74),(-96,35),(-77,2)).arc((-97,-22),(-65,-28)).arc((-61,-44),(-52,-59)).arc((-19,-32),(20,-30)).arc((53,5),(70,50)).arc((68,51),(66,53)).arc((66,54),(65,54)).arc((67,61),(70,67)).arc((29,72),(-7,51)).arc((-54,39),(-77,0)).arc((-89,25),(-93,51)).arc((-96,52),(-97,54)).arc((-98,54),(-99,53)).close().assemble().finalize().extrude(2))
compound=r.val()
cq.exporters.export(compound, '/data/home/cuiyuehan/project/mesh2cad/ours3/cad_recode_val1000_inference_v1/step/deepcad__0068_00681355.step')
