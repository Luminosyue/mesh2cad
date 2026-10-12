import cadquery as cq
plane = cq.Plane(origin=[-0.00019448458712619987, -3.103791098432976e-05, -0.5], xDir=[0.0, -1.0, 0.0], normal=[0.0, 0.0, 1.0])
result = cq.Workplane(plane).circle(0.03511514662165085).extrude(1.0)
