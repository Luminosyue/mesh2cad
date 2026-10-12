import cadquery as cq
w0=cq.Workplane('ZX',origin=(0,7,0))
r=w0.sketch().segment((-13,-17),(-7,-20)).segment((4,1)).segment((-4,1)).segment((-4,9)).close().assemble().finalize().extrude(-107).union(w0.sketch().arc((-2,15),(10,0),(0,-19)).arc((13,1),(-2,19)).close().assemble().finalize().extrude(-46)).union(w0.sketch().segment((0,3),(5,-7)).arc((10,12),(0,3)).assemble().finalize().extrude(93))