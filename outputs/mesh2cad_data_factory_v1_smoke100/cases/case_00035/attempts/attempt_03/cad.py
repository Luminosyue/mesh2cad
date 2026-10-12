import cadquery as cq
plane = cq.Plane(origin=[0.0, 0.0, -0.04054071754217148], xDir=[0.0, -1.0, 0.0], normal=[0.0, 0.0, 1.0])
result = cq.Workplane(plane).circle(0.4014250636100769).extrude(0.08108143508434296)
