import cadquery as cq
plane = cq.Plane(origin=[-0.011395241927980481, 0.03797483011200711, -0.311320681311943], xDir=[0.0, -1.0, 0.0], normal=[0.0, 0.0, 1.0])
result = cq.Workplane(plane).circle(0.4254506605305641).extrude(0.7297162413597107)
