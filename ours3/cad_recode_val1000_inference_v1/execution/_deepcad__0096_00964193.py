import cadquery as cq
import cadquery as cq
w0=cq.Workplane('XY',origin=(0,0,100))
w1=cq.Workplane('XY',origin=(0,0,54))
r=w0.sketch().segment((-44,1),(-40,-18)).segment((-35,-17)).arc((11,37),(22,-32)).segment((21,-37)).arc((25,-34),(29,-31)).segment((26,-31)).arc((-11,38),(-35,-36)).segment((-35,-17)).segment((-39,-17)).segment((-39,3)).close().assemble().finalize().extrude(-194).union(w0.sketch().arc((-40,2),(-41,-13),(-29,-24)).arc((-35,-11),(-40,2)).assemble().reset().face(w0.sketch().arc((-21,-37),(-10,-42),(1,-44)).segment((-1,-37)).close().assemble()).reset().face(w0.sketch().segment((-14,41),(-12,34)).arc((-1,39),(11,39)).segment((9,44)).close().assemble()).reset().face(w0.sketch().segment((18,-35),(22,-37)).segment((29,-26)).arc((24,-31),(18,-35)).assemble()).reset().face(w0.sketch().arc((26,35),(33,28),(36,22)).segment((32,31)).close().assemble()).finalize().extrude(-71)).union(w1.sketch().arc((-28,-28),(11,-42),(43,-15)).arc((41,-10),(38,-5)).arc((3,-40),(-28,-28)).assemble().finalize().extrude(-154))
compound=r.val()
cq.exporters.export(compound, '/data/home/cuiyuehan/project/mesh2cad/ours3/cad_recode_val1000_inference_v1/step/deepcad__0096_00964193.step')
