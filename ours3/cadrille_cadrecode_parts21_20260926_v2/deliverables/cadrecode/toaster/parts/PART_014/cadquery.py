import cadquery as cq
w0=cq.Workplane('XY',origin=(0,0,70))
w1=cq.Workplane('YZ',origin=(2,0,0))
r=w0.sketch().segment((-8,13),(-3,13)).arc((-2,15),(-1,16)).segment((-4,18)).close().assemble().finalize().extrude(-170).union(w0.workplane(offset=22/2).moveTo(0,1).cylinder(22,3)).union(w0.sketch().segment((1,15),(8,14)).segment((8,19)).arc((4,18),(1,15)).assemble().finalize().extrude(30)).union(w1.sketch().arc((-29,71),(0,70),(28,75)).arc((0,92),(-29,71)).assemble().finalize().extrude(-5))