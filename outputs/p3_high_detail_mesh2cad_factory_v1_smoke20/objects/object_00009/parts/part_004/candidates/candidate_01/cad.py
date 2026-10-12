import cadquery as cq
plane = cq.Plane(origin=[0.0602177536180437, 0.004357982732049959, -0.5], xDir=[0.0, -1.0, 0.0], normal=[0.0, 0.0, 1.0])
result = cq.Workplane(plane).circle(0.35110240446132585).extrude(1.0)
