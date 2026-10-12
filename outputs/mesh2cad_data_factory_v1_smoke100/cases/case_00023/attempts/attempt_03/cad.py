import cadquery as cq
plane = cq.Plane(origin=[0.0, -0.004193158354610205, 0.0], xDir=[0.0, 0.0, 1.0], normal=[0.0, 1.0, 0.0])
result = cq.Workplane(plane).circle(0.26238605566322803).extrude(0.00838631670922041)
