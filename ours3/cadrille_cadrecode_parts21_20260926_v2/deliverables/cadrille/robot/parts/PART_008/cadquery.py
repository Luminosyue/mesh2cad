import cadquery as cq
w0=cq.Workplane('YZ',origin=(-21,0,0))
w1=cq.Workplane('ZX',origin=(0,48,0))
r=w0.workplane(offset=69/2).cylinder(69,97).union(w1.workplane(offset=-74/2).cylinder(74,93))