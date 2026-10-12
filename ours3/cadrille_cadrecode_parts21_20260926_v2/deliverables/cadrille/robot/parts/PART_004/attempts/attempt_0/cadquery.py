import cadquery as cq
w0=cq.Workplane('YZ',origin=(-67,0,0))
w1=cq.Workplane('XY',origin=(0,0,47))
r=w0.workplane(offset=108/2).cylinder(108,98).union(w1.workplane(offset=-87/2).cylinder(87,100))