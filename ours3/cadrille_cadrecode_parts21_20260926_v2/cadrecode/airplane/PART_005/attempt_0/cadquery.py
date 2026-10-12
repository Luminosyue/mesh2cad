import cadquery as cq
w0=cq.Workplane('ZX',origin=(0,-2,0))
w1=cq.Workplane('ZX',origin=(0,-15,0))
r=w0.sketch().segment((-9,-4),(11,-14)).segment((14,-7)).segment((-6,1)).close().assemble().finalize().extrude(-98).union(w0.workplane(offset=-45/2).moveTo(1,0).cylinder(45,12)).union(w0.sketch().segment((-19,7),(-16,4)).segment((-16,5)).segment((-10,5)).segment((-10,1)).segment((-13,1)).segment((-4,-4)).segment((0,0)).arc((0,1),(1,1)).segment((6,6)).segment((-4,14)).arc((-10,11),(-12,15)).close().assemble().finalize().extrude(102)).union(w1.workplane(offset=-35/2).moveTo(1,0).cylinder(35,19))