import cadquery as cq
plane = cq.Plane(origin=[0.011684940965414564, -0.5, -0.0011839232984039026], xDir=[0.0, 0.0, 1.0], normal=[0.0, 1.0, 0.0])
result = cq.Workplane(plane).circle(0.024644068797926053).extrude(1.0)
