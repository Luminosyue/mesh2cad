import cadquery as cq
import cadquery as cq
w0=cq.Workplane('XY',origin=(0,0,-16))
w1=cq.Workplane('XY',origin=(0,0,16))
r=w0.sketch().segment((-100,6),(-89,3)).segment((-89,-18)).segment((-66,-18)).segment((-72,-45)).segment((-59,-48)).segment((-53,-18)).segment((-47,-18)).segment((-47,1)).segment((-28,44)).segment((-56,55)).segment((-62,37)).segment((-89,37)).segment((-89,20)).segment((-95,25)).close().assemble().reset().face(w0.sketch().segment((-42,-34),(-29,-45)).segment((10,1)).arc((36,-13),(58,6)).segment((88,3)).segment((89,7)).segment((59,10)).arc((50,28),(33,38)).segment((44,53)).segment((40,55)).segment((29,40)).arc((1,28),(-1,0)).segment((-29,10)).close().assemble()).push([(30,-29)]).circle(4).finalize().extrude(-4).union(w0.sketch().segment((0,-17),(43,-51)).segment((58,-50)).segment((57,-49)).arc((66,-47),(73,-44)).segment((68,-29)).segment((90,-29)).segment((90,-4)).segment((64,-4)).segment((79,43)).arc((16,41),(2,-17)).close().assemble().finalize().extrude(36)).union(w1.sketch().arc((64,-48),(81,-34),(90,-14)).arc((81,-15),(72,-14)).arc((69,-30),(64,-45)).close().assemble().finalize().extrude(-21))
compound=r.val()
cq.exporters.export(compound, '/data/home/cuiyuehan/project/mesh2cad/ours3/cad_recode_val1000_inference_v1/step/deepcad__0026_00260490.step')
