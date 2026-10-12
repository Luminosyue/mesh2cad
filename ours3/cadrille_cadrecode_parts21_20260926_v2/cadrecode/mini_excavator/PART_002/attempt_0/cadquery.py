import cadquery as cq
w0=cq.Workplane('YZ',origin=(-62,0,0))
w1=cq.Workplane('YZ',origin=(-65,0,0))
r=w0.sketch().arc((-10,-100),(11,-49),(42,-3)).arc((-61,32),(-10,-70)).close().assemble().finalize().extrude(125).union(w0.sketch().arc((-30,75),(-25,-12),(49,35)).arc((54,41),(58,49)).arc((68,87),(30,94)).arc((-1,93),(-30,75)).assemble().reset().face(w0.sketch().arc((-25,71),(-1,29),(44,44)).arc((1,52),(-25,71)).assemble(),mode='s').finalize().extrude(127)).union(w1.sketch().arc((-10,-98),(-1,-88),(2,-76)).arc((-43,-18),(-10,-98)).assemble().finalize().extrude(127))