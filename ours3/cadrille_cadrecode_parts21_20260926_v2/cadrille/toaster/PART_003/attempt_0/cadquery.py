import cadquery as cq
w0=cq.Workplane('ZX',origin=(0,-100,0))
w1=cq.Workplane('YZ',origin=(-3,0,0))
r=w0.sketch().arc((-12,2),(-10,-1),(-8,-3)).segment((1,-14)).segment((1,-12)).arc((-3,1),(1,14)).close().assemble().finalize().extrude(107).union(w1.sketch().arc((88,-12),(93,-7),(97,-2)).arc((91,2),(95,7)).arc((93,10),(90,12)).arc((86,0),(88,-12)).assemble().finalize().extrude(9))