import cadquery as cq
w0=cq.Workplane('YZ',origin=(-36,0,0))
w1=cq.Workplane('ZX',origin=(0,48,0))
r=w0.workplane(offset=92/2).cylinder(92,98).union(w1.workplane(offset=-86/2).moveTo(0,-6).cylinder(86,94))