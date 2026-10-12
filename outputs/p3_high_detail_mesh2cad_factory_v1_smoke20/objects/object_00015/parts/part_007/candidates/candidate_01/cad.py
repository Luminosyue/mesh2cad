import cadquery as cq
plane = cq.Plane(origin=[-0.0074159756147851585, -0.10699775815010071, 0.011585385411786806], xDir=[0.0, 0.0, 1.0], normal=[0.0, 1.0, 0.0])
result = cq.Workplane(plane).circle(0.39922271408799526).extrude(0.21399551630020142)
