import cadquery as cq
plane = cq.Plane(origin=[0.0, -0.06250015646219254, 0.0], xDir=[0.0, 0.0, 1.0], normal=[0.0, 1.0, 0.0])
p0 = cq.Workplane(plane).polyline([[-0.5, 0.06250002235174179], [-0.5, -0.06250002235174179], [0.5, -0.06250002235174179]]).close().extrude(0.12500031292438507)
result = p0
