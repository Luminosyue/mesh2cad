import cadquery as cq
w0=cq.Workplane('YZ',origin=(-31,0,0))
r=w0.workplane(offset=-7/2).cylinder(7,99).union(w0.sketch().circle(100).circle(93,mode='s').finalize().extrude(68))