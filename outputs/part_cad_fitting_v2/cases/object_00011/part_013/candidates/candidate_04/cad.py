import cadquery as cq
plane = cq.Plane(origin=[-0.00014584080215701665, 0.00014041247432224768, -0.5], xDir=[0.0, -1.0, 0.0], normal=[0.0, 0.0, 1.0])
result = cq.Workplane(plane).circle(0.03400869096518673).extrude(1.0)
