import cadquery as cq
w0=cq.Workplane('YZ',origin=(-33,0,0))
w1=cq.Workplane('XY',origin=(0,0,55))
r=w0.sketch().circle(100).circle(4,mode='s').finalize().extrude(66).union(w1.workplane(offset=-135/2).cylinder(135,93))