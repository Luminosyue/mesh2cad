import cadquery as cq
w0=cq.Workplane('YZ',origin=(-93,0,0))
r=w0.sketch().circle(100).circle(93,mode='s').finalize().extrude(-7).union(w0.sketch().circle(100).circle(93,mode='s').finalize().extrude(68)).union(w0.workplane(offset=193/2).moveTo(0,1).cylinder(193,3))