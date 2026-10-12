import cadquery as cq
w0=cq.Workplane('YZ',origin=(27,0,0))
w1=cq.Workplane('XY',origin=(0,0,-34))
r=w0.workplane(offset=-119/2).cylinder(119,75).union(w0.workplane(offset=-80/2).cylinder(80,98)).union(w1.workplane(offset=80/2).cylinder(80,100))