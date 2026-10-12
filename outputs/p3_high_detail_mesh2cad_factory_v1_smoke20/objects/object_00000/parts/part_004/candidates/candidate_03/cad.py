import cadquery as cq
plane = cq.Plane(origin=[0.050173696504912726, -0.5, -0.013181256055969162], xDir=[0.0, 0.0, 1.0], normal=[0.0, 1.0, 0.0])
result = cq.Workplane(plane).circle(0.12394701977821485).extrude(1.0)
