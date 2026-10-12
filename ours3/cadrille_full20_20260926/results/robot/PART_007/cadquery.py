import cadquery as cq
w0=cq.Workplane('YZ',origin=(28,0,0))
w1=cq.Workplane('ZX',origin=(0,26,0))
r=w0.workplane(offset=-100/2).cylinder(100,97).union(w0.workplane(offset=-68/2).cylinder(68,100)).union(w1.workplane(offset=-61/2).moveTo(0,-7).cylinder(61,93))