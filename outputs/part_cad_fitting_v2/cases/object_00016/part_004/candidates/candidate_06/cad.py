import cadquery as cq
plane = cq.Plane(origin=[0.011538980681952717, -4.341752774326177, 0.028956205174249055], xDir=[1.0, 0.0, 0.0], normal=[0.0, 0.0, 1.0])
result = cq.Workplane(plane).sphere(4.4449752543743175)
