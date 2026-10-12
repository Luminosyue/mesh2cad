import cadquery as cq
import cadquery as cq
w0=cq.Workplane('ZX',origin=(0,40,0))
w1=cq.Workplane('ZX',origin=(0,34,0))
r=w0.sketch().segment((-60,-100),(15,-100)).segment((15,-99)).arc((39,-86),(53,-62)).arc((3,-50),(22,-10)).arc((19,-10),(15,-9)).segment((15,-20)).segment((-60,-20)).close().assemble().reset().face(w0.sketch().arc((28,-42),(34,-50),(38,-59)).arc((40,-56),(42,-53)).arc((35,-48),(28,-42)).assemble(),mode='s').finalize().extrude(-80).union(w0.sketch().segment((-60,-27),(-23,-27)).segment((-23,2)).segment((25,-14)).segment((25,-1)).segment((-56,23)).segment((-55,26)).segment((-60,26)).close().assemble().reset().face(w0.sketch().segment((-60,66),(-40,55)).segment((-40,100)).segment((-60,100)).close().assemble()).reset().face(w0.sketch().segment((-21,65),(-14,62)).segment((-14,63)).close().assemble()).finalize().extrude(-75)).union(w0.sketch().arc((1,-68),(59,-51),(10,-10)).segment((10,-68)).close().assemble().finalize().extrude(-58)).union(w1.sketch().arc((-33,90),(-23,67),(-20,43)).arc((-9,56),(-14,72)).arc((-22,72),(-20,80)).arc((-27,86),(-33,90)).assemble().finalize().extrude(-34))
compound=r.val()
cq.exporters.export(compound, '/data/home/cuiyuehan/project/mesh2cad/ours3/cad_recode_val1000_inference_v1/step/deepcad__0033_00332120.step')
