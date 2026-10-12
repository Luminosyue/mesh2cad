import cadquery as cq
plane = cq.Plane(origin=[0.1989654012868118, 0.07456747271271139, -0.5], xDir=[0.0, -1.0, 0.0], normal=[0.0, 0.0, 1.0])
result = cq.Workplane(plane).circle(0.3680121139949377).extrude(1.0)
