import cadquery as cq
plane = cq.Plane(origin=[-0.006125630406986418, -0.48714465195364104, 0.0007208339988222883], xDir=[0.0, 0.0, 1.0], normal=[0.0, 1.0, 0.0])
result = cq.Workplane(plane).circle(0.023982735880503425).extrude(1.0)
