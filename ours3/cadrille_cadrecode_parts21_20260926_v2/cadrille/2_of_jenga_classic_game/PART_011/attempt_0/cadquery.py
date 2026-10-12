import cadquery as cq
w0=cq.Workplane('ZX',origin=(0,100,0))
r=w0.sketch().segment((-30,-44),(29,-49)).segment((30,-29)).arc((0,-37),(-30,-29)).close().assemble().finalize().extrude(-200).union(w0.sketch().segment((-30,-27),(30,-27)).segment((30,44)).segment((-24,49)).segment((-24,43)).segment((-30,43)).close().assemble().finalize().extrude(-197))