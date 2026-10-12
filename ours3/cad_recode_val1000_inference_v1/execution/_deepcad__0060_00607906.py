import cadquery as cq
import cadquery as cq
w0=cq.Workplane('XY',origin=(0,0,-41))
w1=cq.Workplane('XY',origin=(0,0,-39))
r=w0.sketch().arc((-95,-25),(-67,-1),(-30,-10)).arc((-32,49),(-84,33)).arc((-81,31),(-79,28)).arc((-70,28),(-62,24)).arc((-58,25),(-54,25)).arc((-49,30),(-43,34)).arc((-87,38),(-95,-5)).arc((-100,-15),(-95,-25)).assemble().finalize().extrude(27).union(w0.sketch().segment((-52,9),(-36,-47)).segment((-13,-41)).arc((10,-74),(50,-66)).arc((98,-11),(68,54)).segment((68,41)).arc((85,0),(68,-41)).segment((68,-45)).segment((61,-45)).arc((29,-61),(-5,-53)).segment((-29,30)).segment((-22,32)).arc((-23,33),(-23,34)).segment((-30,31)).arc((-34,23),(-36,12)).close().assemble().reset().face(w0.sketch().segment((-17,54),(39,61)).arc((11,74),(-17,64)).close().assemble()).finalize().extrude(82)).union(w1.sketch().arc((-37,-45),(10,-74),(64,-63)).arc((50,-54),(41,-41)).arc((10,-61),(-25,-45)).close().assemble().finalize().extrude(55))
compound=r.val()
cq.exporters.export(compound, '/data/home/cuiyuehan/project/mesh2cad/ours3/cad_recode_val1000_inference_v1/step/deepcad__0060_00607906.step')
