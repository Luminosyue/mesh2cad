import cadquery as cq
plane = cq.Plane(origin=[0.005586559313490436, 9.794893018839643e-05, -0.5], xDir=[0.0, -1.0, 0.0], normal=[0.0, 0.0, 1.0])
result = cq.Workplane(plane).circle(0.03449766914656994).extrude(1.0)
