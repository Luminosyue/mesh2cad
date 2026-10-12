import cadquery as cq
w0=cq.Workplane('XY',origin=(0,0,100))
w1=cq.Workplane('ZX',origin=(0,-73,0))
r=w0.sketch().segment((-4,-72),(3,-73)).segment((3,-2)).segment((-4,-2)).segment((-4,-5)).arc((0,-12),(-1,-20)).segment((-1,-55)).segment((-4,-55)).close().assemble().finalize().extrude(-200).union(w1.sketch().arc((47,-4),(50,-6),(53,-6)).arc((66,0),(75,-5)).arc((87,-5),(100,0)).arc((99,1),(99,3)).arc((98,3),(97,4)).arc((73,4),(47,0)).close().assemble().finalize().extrude(145))