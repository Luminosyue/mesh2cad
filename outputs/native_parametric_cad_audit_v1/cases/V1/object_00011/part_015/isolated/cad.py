import cadquery as cq
plane = cq.Plane(origin=[0.006224011884432147, 0.00024784824447593933, -0.5], xDir=[0.0, -1.0, 0.0], normal=[0.0, 0.0, 1.0])
result = cq.Workplane(plane).circle(0.037208345699049045).extrude(1.0)
