import cadquery as cq
w0=cq.Workplane('ZX',origin=(0,21,0))
w0=cq.Workplane('ZX',origin=(0,7,0))
r=w0.workplane(offset=-121/2).moveTo(-78,-91).cylinder(121,3).union(w0.sketch().segment((-100,-83),(-81,-91)).segment((-77,-84)).segment((-78,-72)).close().assemble().finalize().extrude(79)).union(w0.workplane(offset=79/2).moveTo(-92,-77).cylinder(79,6))