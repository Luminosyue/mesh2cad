import cadquery as cq
w0=cq.Workplane('ZX',origin=(0,100,0))
r=w0.sketch().segment((-8,-4),(6,-5)).segment((7,0)).arc((6,3),(7,6)).segment((7,7)).segment((-7,8)).close().assemble().finalize().extrude(-200).union(w0.sketch().segment((-9,5),(-8,-7)).segment((8,-6)).segment((7,7)).close().assemble().finalize().extrude(-100))