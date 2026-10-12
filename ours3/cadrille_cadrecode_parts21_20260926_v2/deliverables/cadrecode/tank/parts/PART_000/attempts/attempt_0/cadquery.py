import cadquery as cq
w0=cq.Workplane('ZX',origin=(0,-79,0))
r=w0.workplane(offset=-21/2).cylinder(21,5).union(w0.workplane(offset=179/2).cylinder(179,2))