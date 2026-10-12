import cadquery as cq
import cadquery as cq
w0=cq.Workplane('XY',origin=(0,0,-45))
r=w0.sketch().arc((-97,-25),(11,5),(67,-74)).arc((37,93),(-97,-25)).assemble().finalize().extrude(-1).union(w0.sketch().arc((-70,-72),(-1,-100),(68,-73)).arc((89,-46),(99,-14)).segment((100,-14)).segment((100,14)).segment((99,14)).arc((89,46),(65,74)).arc((62,78),(58,81)).arc((40,87),(21,91)).arc((23,95),(25,97)).arc((-22,93),(-65,76)).arc((-81,58),(-93,37)).arc((-100,0),(-90,-37)).arc((-89,-47),(-86,-56)).arc((-77,-64),(-68,-72)).close().assemble().reset().face(w0.sketch().segment((-81,-1),(-70,-1)).arc((-70,14),(-68,29)).segment((-81,29)).close().assemble(),mode='s').push([(15,-47)]).circle(27,mode='s').finalize().extrude(91))
compound=r.val()
cq.exporters.export(compound, '/data/home/cuiyuehan/project/mesh2cad/ours3/cad_recode_val1000_inference_v1/step/deepcad__0061_00611907.step')
