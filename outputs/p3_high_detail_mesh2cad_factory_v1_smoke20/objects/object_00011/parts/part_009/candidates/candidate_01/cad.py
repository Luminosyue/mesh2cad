import cadquery as cq
plane = cq.Plane(origin=[0.004568165538941946, -0.0003149241317908234, -0.5], xDir=[0.0, -1.0, 0.0], normal=[0.0, 0.0, 1.0])
result = cq.Workplane(plane).circle(0.037670793969276424).extrude(1.0)
