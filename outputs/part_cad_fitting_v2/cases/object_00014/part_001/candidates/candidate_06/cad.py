import cadquery as cq
plane = cq.Plane(origin=[0.9682981360331359, 0.25658117239363676, 0.024177307843002142], xDir=[1.0, 0.0, 0.0], normal=[0.0, 0.0, 1.0])
result = cq.Workplane(plane).sphere(1.1009212732946996)
