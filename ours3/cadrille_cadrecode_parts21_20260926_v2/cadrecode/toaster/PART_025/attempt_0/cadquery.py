import cadquery as cq
w0=cq.Workplane('XY',origin=(0,0,75))
r=w0.sketch().segment((4,-12),(4,8)).segment((4,9)).arc((-4,-5),(4,-12)).assemble().finalize().extrude(-175).union(w0.workplane(offset=25/2).moveTo(2,0).cylinder(25,4))