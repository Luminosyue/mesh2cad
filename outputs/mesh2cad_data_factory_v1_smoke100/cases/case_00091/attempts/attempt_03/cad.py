import cadquery as cq
plane = cq.Plane(origin=[0.0, -0.35571375489234924, 0.0], xDir=[0.0, 0.0, 1.0], normal=[0.0, 1.0, 0.0])
result = cq.Workplane(plane).circle(0.43463730812072754).extrude(0.7114275097846985)
