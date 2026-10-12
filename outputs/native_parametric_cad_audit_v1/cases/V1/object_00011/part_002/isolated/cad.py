import cadquery as cq
plane = cq.Plane(origin=[0.007909687459428586, -0.00017573883028645088, -0.5], xDir=[0.0, -1.0, 0.0], normal=[0.0, 0.0, 1.0])
result = cq.Workplane(plane).circle(0.03656586110061772).extrude(1.0)
