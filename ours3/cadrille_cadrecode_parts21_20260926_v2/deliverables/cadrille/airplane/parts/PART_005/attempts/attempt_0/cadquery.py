import cadquery as cq
w0=cq.Workplane('ZX',origin=(0,-26,0))
w1=cq.Workplane('ZX',origin=(0,-56,0))
r=w0.sketch().segment((-10,-5),(8,-14)).segment((10,-11)).segment((-8,-2)).close().assemble().finalize().extrude(-74).union(w0.sketch().segment((-18,1),(6,-8)).segment((15,10)).segment((1,14)).segment((1,10)).segment((-13,10)).segment((-13,12)).close().assemble().finalize().extrude(57)).union(w0.sketch().segment((-19,12),(-16,4)).segment((-4,10)).segment((-13,15)).close().assemble().finalize().extrude(126)).union(w1.workplane(offset=40/2).moveTo(0,-1).cylinder(40,10))