import cadquery as cq
w0=cq.Workplane('ZX',origin=(0,-59,0))
w1=cq.Workplane('YZ',origin=(-98,0,0))
r=w0.sketch().segment((-21,94),(-20,57)).arc((-21,47),(-20,37)).segment((-20,-100)).segment((20,-99)).segment((20,-37)).arc((21,-27),(20,-17)).segment((20,95)).close().assemble().finalize().extrude(92).union(w1.sketch().segment((-59,-18),(-10,-18)).arc((0,-21),(10,-18)).segment((59,-18)).segment((59,18)).segment((10,18)).arc((0,21),(-10,18)).segment((-59,18)).close().assemble().finalize().extrude(198))