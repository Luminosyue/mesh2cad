import cadquery as cq
plane = cq.Plane(origin=[19.67541445085681, -0.1697186517768417, -25.64335275012293], xDir=[1.0, 0.0, 0.0], normal=[0.0, 0.0, 1.0])
result = cq.Workplane(plane).sphere(32.37002435070588)
