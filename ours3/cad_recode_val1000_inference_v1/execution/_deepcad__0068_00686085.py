import cadquery as cq
import cadquery as cq
w0=cq.Workplane('ZX',origin=(0,-9,0))
w1=cq.Workplane('YZ',origin=(49,0,0))
r=w0.sketch().segment((-21,2),(-14,2)).segment((-14,10)).arc((17,10),(23,41)).arc((1,13),(-21,41)).arc((-22,31),(-21,21)).close().assemble().reset().face(w0.sketch().segment((53,-28),(54,-28)).segment((94,49)).segment((79,55)).arc((78,53),(77,52)).segment((77,49)).segment((76,49)).arc((68,18),(53,-10)).close().assemble()).reset().face(w0.sketch().arc((56,57),(60,57),(63,56)).segment((63,63)).segment((87,63)).segment((87,49)).segment((89,49)).segment((89,56)).segment((93,50)).arc((89,73),(74,91)).close().assemble()).finalize().extrude(-9).union(w0.sketch().segment((-94,-100),(9,-100)).segment((9,-90)).segment((41,-90)).segment((41,24)).segment((9,24)).segment((9,34)).segment((-25,34)).arc((-37,-14),(-73,-45)).segment((-73,-61)).segment((-86,-61)).segment((-86,-45)).arc((-90,-43),(-94,-40)).close().assemble().push([(-39,-71)]).circle(18,mode='s').finalize().extrude(27)).union(w1.sketch().arc((-12,24),(-17,-10),(-10,23)).arc((-11,23),(-12,24)).assemble().finalize().extrude(14))
compound=r.val()
cq.exporters.export(compound, '/data/home/cuiyuehan/project/mesh2cad/ours3/cad_recode_val1000_inference_v1/step/deepcad__0068_00686085.step')
