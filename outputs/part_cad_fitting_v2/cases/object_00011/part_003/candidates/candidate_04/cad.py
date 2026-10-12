import cadquery as cq
plane = cq.Plane(origin=[0.0113474074073713, 6.281995117038277e-05, -0.5], xDir=[0.0, -1.0, 0.0], normal=[0.0, 0.0, 1.0])
result = cq.Workplane(plane).circle(0.03375911322354322).extrude(1.0)
