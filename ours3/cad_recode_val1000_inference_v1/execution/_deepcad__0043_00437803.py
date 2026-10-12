import cadquery as cq
import cadquery as cq
w0=cq.Workplane('ZX',origin=(0,-52,0))
r=w0.sketch().segment((-72,-100),(72,-100)).segment((72,91)).segment((11,58)).segment((-10,95)).segment((-10,63)).segment((13,63)).segment((13,54)).segment((1,54)).segment((1,14)).segment((-34,14)).segment((-34,54)).segment((-46,54)).segment((-46,63)).segment((-72,63)).close().assemble().reset().face(w0.sketch().segment((-72,-73),(-66,-73)).segment((-66,-64)).segment((-72,-65)).close().assemble(),mode='s').reset().face(w0.sketch().segment((-72,-38),(-34,-38)).segment((-34,-32)).segment((-72,-32)).close().assemble(),mode='s').finalize().extrude(104).union(w0.sketch().segment((-72,-100),(72,-100)).segment((72,100)).segment((-72,100)).segment((-72,84)).arc((-34,54),(-72,24)).close().assemble().push([(0,-19)]).circle(20,mode='s').finalize().extrude(104))
compound=r.val()
cq.exporters.export(compound, '/data/home/cuiyuehan/project/mesh2cad/ours3/cad_recode_val1000_inference_v1/step/deepcad__0043_00437803.step')
