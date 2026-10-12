import cadquery as cq
plane = cq.Plane(origin=[-2034.151353371004, -0.4928031395199928, -0.9852148708851323], xDir=[1.0, 0.0, 0.0], normal=[0.0, 0.0, 1.0])
result = cq.Workplane(plane).sphere(2034.1519330058647)
