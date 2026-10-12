import cadquery as cq
w0=cq.Workplane('ZX',origin=(0,100,0))
w1=cq.Workplane('YZ',origin=(3,0,0))
r=w0.sketch().segment((-21,4),(-17,2)).arc((-5,2),(-6,-3)).segment((1,-6)).arc((2,2),(10,0)).segment((21,6)).arc((0,7),(-21,4)).assemble().finalize().extrude(-177).union(w1.sketch().segment((-99,-17),(-94,-17)).segment((-94,-11)).arc((-77,0),(-94,11)).segment((-99,11)).segment((-99,-11)).close().assemble().finalize().extrude(3))