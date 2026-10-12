import cadquery as cq
plane = cq.Plane(origin=[0.07222927604237031, 0.0381217329063488, -1.760438606155356], xDir=[1.0, 0.0, 0.0], normal=[0.0, 0.0, 1.0])
result = cq.Workplane(plane).sphere(1.8858761052854431)
