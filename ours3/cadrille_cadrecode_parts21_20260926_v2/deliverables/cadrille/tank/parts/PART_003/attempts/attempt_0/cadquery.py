import cadquery as cq
w0=cq.Workplane('ZX',origin=(0,-100,0))
r=w0.sketch().segment((-5,1),(-2,0)).segment((-2,-2)).segment((2,-2)).segment((2,0)).segment((5,4)).segment((2,4)).segment((2,6)).segment((-2,6)).segment((-2,4)).close().assemble().finalize().extrude(17).union(w0.workplane(offset=200/2).moveTo(0,-4).cylinder(200,2))