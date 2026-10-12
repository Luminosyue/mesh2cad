import cadquery as cq
plane = cq.Plane(origin=[0.0011762298998142869, -0.5, -0.003944646452231547], xDir=[0.0, 0.0, 1.0], normal=[0.0, 1.0, 0.0])
result = cq.Workplane(plane).circle(0.012911188650918198).extrude(1.0)
