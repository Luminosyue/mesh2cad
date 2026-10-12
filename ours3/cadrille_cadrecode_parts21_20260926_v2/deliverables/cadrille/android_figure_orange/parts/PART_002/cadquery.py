import cadquery as cq
w0=cq.Workplane('ZX',origin=(0,-1,0))
w1=cq.Workplane('XY',origin=(0,0,44))
r=w0.workplane(offset=-55/2).moveTo(65,-7).cylinder(55,30).union(w0.sketch().segment((-100,1),(-96,-2)).arc((-78,-29),(-46,-39)).segment((-42,-42)).segment((-39,-37)).arc((-10,-19),(-2,14)).segment((1,19)).segment((-3,22)).arc((-21,49),(-53,59)).segment((-57,62)).segment((-60,57)).arc((-88,39),(-98,7)).close().assemble().finalize().extrude(46)).union(w1.workplane(offset=-114/2).moveTo(-3,2).cylinder(114,37))