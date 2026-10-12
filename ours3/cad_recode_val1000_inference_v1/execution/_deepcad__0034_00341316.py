import cadquery as cq
import cadquery as cq
w0=cq.Workplane('ZX',origin=(0,-39,0))
w1=cq.Workplane('XY',origin=(0,0,47))
r=w0.sketch().segment((-47,-34),(-43,-34)).segment((-43,-24)).segment((-37,-24)).arc((-32,10),(-13,37)).segment((-13,48)).segment((1,48)).arc((22,56),(43,48)).segment((47,48)).segment((47,63)).segment((-47,63)).close().assemble().reset().face(w0.sketch().segment((-47,-100),(-7,-100)).segment((-7,-98)).arc((-41,-76),(-47,-34)).close().assemble()).reset().face(w0.sketch().arc((1,-45),(22,-62),(43,-45)).segment((37,-45)).arc((22,-52),(7,-45)).close().assemble()).reset().face(w0.sketch().segment((1,-10),(7,-10)).arc((22,-3),(37,-10)).segment((47,-10)).segment((47,100)).segment((1,100)).arc((13,94),(21,85)).arc((22,84),(23,83)).arc((32,51),(1,37)).close().assemble()).finalize().extrude(78).union(w1.sketch().arc((-95,-30),(-72,-14),(-45,-14)).arc((-49,12),(-29,29)).segment((-29,39)).segment((59,39)).arc((14,40),(-23,17)).arc((-37,28),(-55,34)).arc((-56,37),(-58,39)).segment((-65,39)).segment((-65,34)).arc((-79,26),(-90,13)).arc((-86,1),(-94,10)).arc((-96,-10),(-95,-30)).assemble().finalize().extrude(-94))
compound=r.val()
cq.exporters.export(compound, '/data/home/cuiyuehan/project/mesh2cad/ours3/cad_recode_val1000_inference_v1/step/deepcad__0034_00341316.step')
