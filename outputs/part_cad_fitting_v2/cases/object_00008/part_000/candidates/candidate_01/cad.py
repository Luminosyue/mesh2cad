import cadquery as cq
plane = cq.Plane(origin=[-0.01775696057334956, 0.012630832782420028, -0.08], xDir=[0.0, -1.0, 0.0], normal=[0.0, 0.0, 1.0])
result = cq.Workplane(plane).box(1.0, 0.935684084892273, 0.9333755373954773)
