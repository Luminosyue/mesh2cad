import cadquery as cq
w0=cq.Workplane('YZ',origin=(-47,0,0))
w1=cq.Workplane('ZX',origin=(0,42,0))
r=w0.workplane(offset=117/2).cylinder(117,97).union(w1.workplane(offset=-776/2).cylinder(76,100))