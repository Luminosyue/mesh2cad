import cadquery as cq
w0=cq.Workplane('YZ',origin=(33,0,0))
w1=cq.Workplane('XY',origin=(0,0,37))
r=w0.workplane(offset=-102/2).cylinder(102,99).union(w0.workplane(offset=44/2).cylinder(44,99)).union(w1.workplane(offset=-86/2).cylinder(86,100))