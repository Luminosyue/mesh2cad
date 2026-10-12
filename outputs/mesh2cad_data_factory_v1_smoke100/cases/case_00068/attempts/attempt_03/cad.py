import cadquery as cq
plane = cq.Plane(origin=[0.0, -0.3742212951183319, 0.0], xDir=[0.0, 0.0, 1.0], normal=[0.0, 1.0, 0.0])
result = cq.Workplane(plane).circle(0.41095706820487976).extrude(0.7484425902366638)
