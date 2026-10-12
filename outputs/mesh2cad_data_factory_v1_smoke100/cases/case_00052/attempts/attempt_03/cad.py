import cadquery as cq
plane = cq.Plane(origin=[0.0, -0.015407432802021503, 0.0], xDir=[0.0, 0.0, 1.0], normal=[0.0, 1.0, 0.0])
result = cq.Workplane(plane).circle(0.3368576318025589).extrude(0.030814865604043007)
