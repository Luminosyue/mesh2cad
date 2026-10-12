import cadquery as cq
w0=cq.Workplane('XY',origin=(0,0,97))
w1=cq.Workplane('ZX',origin=(0,95,0))
r=w0.workplane(offset=-194/2).moveTo(-5,47).cylinder(194,3).union(w0.sketch().segment((0,97),(4,89)).segment((7,90)).segment((3,100)).close().assemble().finalize().extrude(-33)).union(w0.workplane(offset=-16/2).moveTo(4,75).cylinder(16,2)).union(w1.workplane(offset=-195/2).moveTo(83,-1).cylinder(195,4))