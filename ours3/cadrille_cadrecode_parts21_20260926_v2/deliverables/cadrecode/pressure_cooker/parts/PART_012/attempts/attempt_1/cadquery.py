import cadquery as cq
w0=cq.Workplane('XY',origin=(0,0,-10))
w1=cq.Workplane('XY',origin=(0,0,-8))
r=w0.sketch().segment((-100,-48),(-98,-54)).segment((-35,35)).arc((-36,37),(-37,41)).arc((-77,5),(-95,-47)).close().assemble().finalize().extrude(18).union(w1.sketch().arc((-24,43),(43,47),(100,19)).arc((44,52),(-24,43)).assemble().finalize().extrude(18))