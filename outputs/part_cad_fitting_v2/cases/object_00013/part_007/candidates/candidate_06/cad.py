import cadquery as cq
plane = cq.Plane(origin=[0.0462332662161684, 34.49133995720431, 0.8800116219086526], xDir=[1.0, 0.0, 0.0], normal=[0.0, 0.0, 1.0])
result = cq.Workplane(plane).sphere(34.49302224711673)
