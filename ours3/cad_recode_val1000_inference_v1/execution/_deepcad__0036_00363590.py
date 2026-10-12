import cadquery as cq
import cadquery as cq
w0=cq.Workplane('XY',origin=(0,0,60))
w1=cq.Workplane('XY',origin=(0,0,46))
r=w0.sketch().arc((-78,59),(-99,5),(-76,-49)).arc((-75,-66),(-66,-79)).segment((-66,-67)).arc((-72,-60),(-76,-52)).arc((-77,-51),(-78,-49)).close().assemble().reset().face(w0.sketch().arc((-66,-49),(-1,53),(76,-49)).arc((77,-57),(72,-64)).arc((73,-67),(73,-69)).arc((99,-5),(78,59)).segment((78,57)).arc((72,69),(66,79)).segment((66,67)).arc((72,60),(76,52)).segment((89,43)).segment((78,27)).segment((78,5)).arc((72,-6),(76,-17)).arc((72,-26),(66,-34)).segment((66,-17)).arc((72,-6),(78,5)).segment((78,27)).arc((72,34),(76,42)).arc((72,69),(53,82)).segment((32,94)).segment((32,93)).arc((-30,93),(-78,59)).assemble()).reset().face(w0.sketch().arc((-46,-87),(16,-97),(73,-69)).segment((66,-67)).arc((30,-94),(-14,-87)).close().assemble()).finalize().extrude(-120).union(w0.sketch().push([(14,0)]).circle(51).circle(36,mode='s').finalize().extrude(-83)).union(w1.workplane(offset=-79/2).moveTo(81,-55).cylinder(79,8))
compound=r.val()
cq.exporters.export(compound, '/data/home/cuiyuehan/project/mesh2cad/ours3/cad_recode_val1000_inference_v1/step/deepcad__0036_00363590.step')
