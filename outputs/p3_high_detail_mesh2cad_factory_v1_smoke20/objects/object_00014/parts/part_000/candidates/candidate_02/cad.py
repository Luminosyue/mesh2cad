import cadquery as cq
plane = cq.Plane(origin=[0.0006046302438264817, -0.15121695619955614, -0.07732706516981125], xDir=[0.0, -1.0, 0.0], normal=[0.0, 0.0, 1.0])
result = cq.Workplane(plane).circle(0.43155345066122813).extrude(0.1546541303396225)
