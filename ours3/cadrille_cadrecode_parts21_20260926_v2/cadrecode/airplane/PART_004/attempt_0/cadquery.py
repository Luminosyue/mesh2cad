import cadquery as cq
w0=cq.Workplane('YZ',origin=(-97,0,0))
w1=cq.Workplane('YZ',origin=(-96,0,0))
r=w0.sketch().segment((36,-13),(58,-19)).segment((60,-13)).close().assemble().finalize().extrude(23).union(w0.sketch().segment((-59,7),(34,-9)).arc((-10,14),(-59,15)).close().assemble().finalize().extrude(187)).union(w1.sketch().arc((-60,12),(-5,5),(34,-9)).arc((-4,12),(-45,19)).arc((-52,16),(-60,12)).assemble().finalize().extrude(182))