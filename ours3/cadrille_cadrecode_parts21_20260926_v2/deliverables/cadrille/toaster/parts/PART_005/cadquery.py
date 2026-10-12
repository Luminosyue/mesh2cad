import cadquery as cq
w0=cq.Workplane('ZX',origin=(0,100,0))
w1=cq.Workplane('YZ',origin=(-4,0,0))
r=w0.sketch().arc((-2,-1),(2,-3),(4,2)).close().assemble().finalize().extrude(-200).union(w0.workplane(offset=-26/2).moveTo(5,0).cylinder(26,4)).union(w1.sketch().arc((-34,-5),(-33,-5),(-33,-6)).arc((-31,-3),(-34,-5)).assemble().finalize().extrude(4))