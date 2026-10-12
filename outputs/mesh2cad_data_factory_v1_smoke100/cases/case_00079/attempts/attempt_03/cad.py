import cadquery as cq
plane = cq.Plane(origin=[0.0, 0.0, -0.36909767985343933], xDir=[0.0, -1.0, 0.0], normal=[0.0, 0.0, 1.0])
result = cq.Workplane(plane).circle(0.427138015627861).extrude(0.7381953597068787)
