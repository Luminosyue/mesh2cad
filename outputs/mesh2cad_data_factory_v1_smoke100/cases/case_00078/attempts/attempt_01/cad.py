import cadquery as cq
plane = cq.Plane(origin=[0.0, -0.5, 0.0], xDir=[0.0, 0.0, 1.0], normal=[0.0, 1.0, 0.0])
result = cq.Workplane(plane).circle(0.3314465135335922).extrude(1.0)
