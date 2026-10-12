import cadquery as cq
w0=cq.Workplane('ZX',origin=(0,-22,0))
w1=cq.Workplane('XY',origin=(0,0,-32))
r=w0.workplane(offset=-57/2).cylinder(57,77).union(w0.workplane(offset=69/2).cylinder(69,100)).union(w0.workplane(offset=120/2).cylinder(120,33)).union(w1.workplane(offset=64/2).cylinder(64,99))