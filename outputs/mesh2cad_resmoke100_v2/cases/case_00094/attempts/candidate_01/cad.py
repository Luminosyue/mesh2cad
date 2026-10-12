import cadquery as cq
plane = cq.Plane(origin=[0.0, 0.0, -0.4998169243335724], xDir=[0.0, -1.0, 0.0], normal=[0.0, 0.0, 1.0])
p0 = cq.Workplane(plane).polyline([[-0.5, 0.499999850988388], [0.5, 0.499999850988388], [0.5, -0.49999985098838806], [-0.5, -0.49999985098838806]]).close().extrude(0.9996338486671448)
result = p0
