import cadquery as cq
w0=cq.Workplane('YZ',origin=(-21,0,0))
w1=cq.Workplane('XY',origin=(0,0,-77))
r=w0.sketch().segment((-100,12),(-18,-100)).segment((73,-30)).segment((1,67)).arc((-39,29),(-94,29)).close().assemble().finalize().extrude(37).union(w0.workplane(offset=120/2).moveTo(0,-1).cylinder(120,76)).union(w1.sketch().push([(-1,0)]).circle(78).circle(48,mode='s').finalize().extrude(174))