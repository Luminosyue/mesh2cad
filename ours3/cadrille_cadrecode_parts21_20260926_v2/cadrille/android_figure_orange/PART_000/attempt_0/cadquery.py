import cadquery as cq
w0=cq.Workplane('XY',origin=(0,0,-53))
w1=cq.Workplane('YZ',origin=(42,0,0))
r=w0.sketch().circle(100).circle(90,mode='s').finalize().extrude(35).union(w0.sketch().segment((46,28),(58,25)).segment((58,27)).segment((46,30)).close().assemble().finalize().extrude(107)).union(w1.workplane(offset=-127/2).moveTo(0,-11).cylinder(127,43))