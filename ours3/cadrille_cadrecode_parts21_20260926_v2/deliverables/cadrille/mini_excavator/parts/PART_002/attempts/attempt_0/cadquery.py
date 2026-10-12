import cadquery as cq
w0=cq.Workplane('YZ',origin=(-62,0,0))
w1=cq.Workplane('YZ',origin=(-64,0,0))
r=w0.sketch().arc((41,97),(-61,-10),(64,63)).arc((66,89),(41,97)).assemble().finalize().extrude(126).union(w1.sketch().arc((-10,-100),(1,-83),(4,-63)).arc((-41,1),(-10,-70)).close().assemble().finalize().extrude(126))