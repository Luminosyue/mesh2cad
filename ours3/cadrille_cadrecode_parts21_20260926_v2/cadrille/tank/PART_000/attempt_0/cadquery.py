import cadquery as cq
w0=cq.Workplane('ZX',origin=(0,-100,0))
r=w0.workplane(offset=14/2).cylinder(14,5).union(w0.workplane(offset=200/2).cylinder(200,2))