import cadquery as cq
plane = cq.Plane(origin=[0.0021904239284188027, -0.13829412428382024, -0.0029204196890049456], xDir=[1.0, 0.0, 0.0], normal=[0.0, 0.0, 1.0])
result = cq.Workplane(plane).sphere(0.4971753614345125)
