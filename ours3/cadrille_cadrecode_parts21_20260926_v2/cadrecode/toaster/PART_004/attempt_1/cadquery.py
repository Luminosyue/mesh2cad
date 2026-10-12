import cadquery as cq
w0=cq.Workplane('ZX',origin=(0,100,0))
r=w0.sketch().segment((0,-1),(0,1)).segment((2,1)).segment((2,-1)).segment((3,-1)).segment((3,-4)).arc((5,3),(0,-1)).assemble().finalize().extrude(-200).union(w0.sketch().segment((-9,4),(5,1)).segment((5,5)).segment((-5,5)).close().assemble().finalize().extrude(-98))