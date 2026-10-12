import cadquery as cq
w0=cq.Workplane('XY',origin=(0,0,99))
r=w0.sketch().segment((-4,-47),(1,-49)).segment((4,47)).segment((-1,49)).close().assemble().finalize().extrude(-198).union(w0.sketch().segment((-3,-47),(3,-47)).segment((3,47)).segment((-3,47)).segment((-3,1)).segment((2,1)).segment((2,-1)).segment((-3,-1)).close().assemble().finalize().extrude(-65))