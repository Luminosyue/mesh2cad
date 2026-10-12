import cadquery as cq
w0=cq.Workplane('YZ',origin=(40,0,0))
w1=cq.Workplane('XY',origin=(0,0,42))
r=w0.workplane(offset=-112/2).cylinder(112,86).union(w0.workplane(offset=-56/2).cylinder(56,92)).union(w1.workplane(offset=-72/2).cylinder(72,100))