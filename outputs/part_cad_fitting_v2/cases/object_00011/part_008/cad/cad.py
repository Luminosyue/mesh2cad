import cadquery as cq
plane = cq.Plane(origin=[-0.008676150992142799, 0.0001148813321206835, -0.5291543804826293], xDir=[0.0, -1.0, 0.0], normal=[0.0, 0.0, 1.0])
result = cq.Workplane(plane).circle(0.036266949144209665).extrude(1.0)
