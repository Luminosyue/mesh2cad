import cadquery as cq
w0=cq.Workplane('ZX',origin=(0,-26,0))
w1=cq.Workplane('XY',origin=(0,0,-25))
r=w0.workplane(offset=-54/2).cylinder(54,83).union(w0.workplane(offset=104/2).cylinder(104,99)).union(w1.workplane(offset=56/2).cylinder(56,100))