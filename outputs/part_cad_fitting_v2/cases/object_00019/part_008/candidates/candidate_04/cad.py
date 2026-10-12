import cadquery as cq
plane = cq.Plane(origin=[0.0016434326026457987, -0.5, -0.0020822272935037667], xDir=[0.0, 0.0, 1.0], normal=[0.0, 1.0, 0.0])
result = cq.Workplane(plane).circle(0.011771861297464175).extrude(1.0)
