import cadquery as cq
plane = cq.Plane(origin=[0.008812546478186568, 6.668571443412833e-05, -0.5], xDir=[0.0, -1.0, 0.0], normal=[0.0, 0.0, 1.0])
result = cq.Workplane(plane).circle(0.03452237205760712).extrude(1.0)
