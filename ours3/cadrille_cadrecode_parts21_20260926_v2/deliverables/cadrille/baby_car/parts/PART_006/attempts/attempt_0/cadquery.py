import cadquery as cq
w0=cq.Workplane('YZ',origin=(43,0,0))
w1=cq.Workplane('ZX',origin=(0,42,0))
r=w0.sketch().segment((-100,1),(-11,-98)).segment((100,-1)).segment((11,98)).close().assemble().finalize().extrude(-52).union(w0.sketch().circle(91).circle(45,mode='s').finalize().extrude(-31)).union(w1.workplane(offset=-87/2).moveTo(0,-1).cylinder(87,47))