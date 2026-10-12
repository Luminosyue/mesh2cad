import cadquery as cq
w0=cq.Workplane('YZ',origin=(31,0,0))
w1=cq.Workplane('ZX',origin=(0,35,0))
r=w0.sketch().segment((-99,-10),(-93,-10)).arc((0,-94),(93,-10)).segment((99,-10)).segment((99,10)).segment((93,10)).arc((0,94),(-93,10)).segment((-99,10)).close().assemble().finalize().extrude(-120).union(w0.workplane(offset=34/2).cylinder(34,92)).union(w1.workplane(offset=-72/2).cylinder(72,100))