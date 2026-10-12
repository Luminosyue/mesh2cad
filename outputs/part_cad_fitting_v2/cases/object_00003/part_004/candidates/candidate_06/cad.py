import cadquery as cq
plane = cq.Plane(origin=[-0.00022461661437276167, 0.03628573164974345, -0.05819560237937711], xDir=[1.0, 0.0, 0.0], normal=[0.0, 0.0, 1.0])
result = cq.Workplane(plane).sphere(0.4609858396819346)
