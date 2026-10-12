import cadquery as cq
plane = cq.Plane(origin=[-0.0007196316819314802, -0.4975026717125093, 0.00024076593264724528], xDir=[0.0, 0.0, 1.0], normal=[0.0, 1.0, 0.0])
result = cq.Workplane(plane).circle(0.012739868894584078).extrude(1.0)
