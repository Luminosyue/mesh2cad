import cadquery as cq
w0=cq.Workplane('XY',origin=(0,0,-17))
w1=cq.Workplane('XY',origin=(0,0,-24))
r=w0.workplane(offset=-20/2).moveTo(0,-2).cylinder(20,32).union(w0.sketch().push([(0,-2)]).circle(93).circle(87,mode='s').finalize().extrude(49)).union(w0.sketch().push([(0,-2)]).circle(80).circle(60,mode='s').finalize().extrude(54)).union(w1.sketch().arc((-65,27),(-93,-21),(-58,-65)).arc((93,2),(-65,27)).assemble().finalize().extrude(57))