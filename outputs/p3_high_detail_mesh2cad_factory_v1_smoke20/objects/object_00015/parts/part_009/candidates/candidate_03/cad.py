import cadquery as cq
plane = cq.Plane(origin=[0.0020993411717324874, -0.009575643845767397, -0.5], xDir=[0.0, -1.0, 0.0], normal=[0.0, 0.0, 1.0])
result = cq.Workplane(plane).circle(0.04280726232893302).extrude(1.0)
