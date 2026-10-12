import cadquery as cq
plane = cq.Plane(origin=[0.00858501237977931, -0.0001853803316175706, -0.5], xDir=[0.0, -1.0, 0.0], normal=[0.0, 0.0, 1.0])
result = cq.Workplane(plane).circle(0.03363703560631063).extrude(1.0)
