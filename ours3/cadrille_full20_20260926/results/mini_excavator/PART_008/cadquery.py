import cadquery as cq
w0=cq.Workplane('YZ',origin=(-24,0,0))
w1=cq.Workplane('YZ',origin=(-98,0,0))
r=w0.sketch().segment((-98,-90),(96,-99)).segment((100,-11)).segment((-98,-3)).close().assemble().finalize().extrude(-75).union(w0.sketch().push([(0,6)]).circle(88).circle(64,mode='s').finalize().extrude(-72)).union(w1.sketch().push([(0,6)]).circle(88).circle(34,mode='s').finalize().extrude(80))