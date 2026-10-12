import cadquery as cq
import cadquery as cq
w0=cq.Workplane('XY',origin=(0,0,-30))
w1=cq.Workplane('XY',origin=(0,0,9))
r=w0.sketch().segment((-44,14),(-41,9)).arc((-37,10),(-33,10)).arc((-24,-15),(-2,-25)).arc((23,-28),(46,-22)).segment((49,-22)).segment((49,-20)).arc((55,-16),(60,-11)).segment((78,10)).segment((75,10)).arc((65,78),(-1,96)).segment((-4,96)).segment((-4,94)).arc((-35,72),(-47,35)).arc((-43,36),(-40,36)).arc((-13,55),(-34,31)).arc((-38,27),(-41,22)).close().assemble().push([(18,36)]).circle(31,mode='s').finalize().extrude(-69).union(w0.sketch().arc((-67,-95),(-47,-80),(-27,-93)).arc((-22,-90),(-18,-86)).segment((-18,-62)).arc((-65,-40),(-67,-95)).assemble().finalize().extrude(2)).union(w0.workplane(offset=129/2).moveTo(-50,-47).cylinder(129,13)).union(w1.sketch().arc((-79,-53),(-70,-89),(-35,-94)).arc((-31,-94),(-28,-91)).arc((-22,-85),(-18,-76)).arc((-50,-87),(-79,-53)).assemble().finalize().extrude(91))
compound=r.val()
cq.exporters.export(compound, '/data/home/cuiyuehan/project/mesh2cad/ours3/cad_recode_val1000_inference_v1/step/deepcad__0077_00774144.step')
