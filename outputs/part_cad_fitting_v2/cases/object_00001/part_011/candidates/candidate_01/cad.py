import cadquery as cq
plane = cq.Plane(origin=[0.08, -0.08, -0.013972073520940103], xDir=[0.0, -1.0, 0.0], normal=[0.0, 0.0, 1.0])
result = cq.Workplane(plane).box(0.8235294818878174, 1.0, 0.19021035730838776)
