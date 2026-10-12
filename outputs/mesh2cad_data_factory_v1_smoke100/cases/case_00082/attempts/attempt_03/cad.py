import cadquery as cq
plane = cq.Plane(origin=[0.0, 0.0, -0.5], xDir=[0.0, -1.0, 0.0], normal=[0.0, 0.0, 1.0])
result = cq.Workplane(plane).circle(0.24652323126792908).extrude(1.0)
