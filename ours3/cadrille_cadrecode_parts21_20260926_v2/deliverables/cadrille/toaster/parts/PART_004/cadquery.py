import cadquery as cq
w0=cq.Workplane('ZX',origin=(0,100,0))
w1=cq.Workplane('XY',origin=(0,0,9))
r=w0.sketch().segment((-5,2),(2,-3)).segment((2,-2)).segment((4,-3)).segment((6,-1)).segment((4,3)).close().assemble().finalize().extrude(-200).union(w1.sketch().arc((3,39),(4,41),(3,43)).close().assemble().finalize().extrude(-17))