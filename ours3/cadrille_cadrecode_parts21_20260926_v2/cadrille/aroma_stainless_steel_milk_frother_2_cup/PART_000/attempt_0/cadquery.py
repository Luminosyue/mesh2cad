import cadquery as cq
w0=cq.Workplane('XY',origin=(0,0,63))
w1=cq.Workplane('ZX',origin=(0,13,0))
r=w0.sketch().segment((-46,-13),(-37,-17)).segment((-20,28)).segment((-29,31)).close().assemble().finalize().extrude(-163).union(w0.sketch().segment((-52,-11),(-44,-14)).segment((-44,-11)).segment((-32,-11)).segment((-32,-16)).segment((-37,-16)).segment((34,-37)).segment((52,8)).segment((-34,37)).close().assemble().finalize().extrude(-141)).union(w0.workplane(offset=35/2).moveTo(-12,3).cylinder(35,29)).union(w1.workplane(offset=-46/2).moveTo(73,12).cylinder(46,15))