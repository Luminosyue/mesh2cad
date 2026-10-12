import cadquery as cq
w0=cq.Workplane('YZ',origin=(99,0,0))
w1=cq.Workplane('YZ',origin=(100,0,0))
r=w0.workplane(offset=-199/2).box(28,100,199).union(w1.workplane(offset=-199/2).box(28,100,199))