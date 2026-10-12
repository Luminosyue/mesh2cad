import cadquery as cq
plane = cq.Plane(origin=[0.0, 0.0, 0.0], xDir=[0.0, 0.0, 1.0], normal=[0.0, 1.0, 0.0])
result = cq.Workplane(plane).box(0.33225512504577637, 0.9935309290885925, 1.0)
