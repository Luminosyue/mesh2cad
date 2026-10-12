import cadquery as cq
plane = cq.Plane(origin=[0.00010794943400394691, -0.013896414330507572, -0.5], xDir=[0.0, -1.0, 0.0], normal=[0.0, 0.0, 1.0])
result = cq.Workplane(plane).circle(0.03602712582839516).extrude(1.0)
