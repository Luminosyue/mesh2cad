import cadquery as cq
w0=cq.Workplane('ZX',origin=(0,-100,0))
w1=cq.Workplane('YZ',origin=(4,0,0))
r=w0.workplane(offset=200/2).moveTo(2,-1).cylinder(200,3).union(w1.workplane(offset=-4/2).moveTo(-69,-4).cylinder(4,2))