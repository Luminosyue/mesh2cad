import cadquery as cq
w0=cq.Workplane('YZ',origin=(-97,0,0))
w1=cq.Workplane('XY',origin=(0,0,91))
r=w0.sketch().segment((78,75),(83,68)).segment((100,78)).segment((95,85)).close().assemble().finalize().extrude(-88).union(w0.workplane(offset=-88/2).moveTo(-87,80).cylinder(88,5)).union(w1.workplane(offset=-191/2).moveTo(-97,47).cylinder(191,4))