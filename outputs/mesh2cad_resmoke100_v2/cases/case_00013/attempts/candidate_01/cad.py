import cadquery as cq
plane = cq.Plane(origin=[0.0, 0.0, -0.5], xDir=[0.0, -1.0, 0.0], normal=[0.0, 0.0, 1.0])
p0 = cq.Workplane(plane).polyline([[0.06250015646219254, 0.06250002235174179], [0.06250015646219254, -0.06250002235174179], [-0.06250015646219254, -0.06250002235174179]]).close().extrude(1.0)
result = p0
