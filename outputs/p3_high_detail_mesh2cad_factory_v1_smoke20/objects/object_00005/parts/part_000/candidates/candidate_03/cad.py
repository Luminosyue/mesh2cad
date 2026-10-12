import cadquery as cq
plane = cq.Plane(origin=[-0.00010503134541381409, -0.004968258318547677, -0.5], xDir=[0.0, -1.0, 0.0], normal=[0.0, 0.0, 1.0])
result = cq.Workplane(plane).circle(0.1948219453940972).extrude(1.0)
