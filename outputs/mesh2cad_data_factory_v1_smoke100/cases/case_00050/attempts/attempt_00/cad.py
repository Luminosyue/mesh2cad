import cadquery as cq
plane = cq.Plane(origin=[0.0, 0.0, -0.4721512496471405], xDir=[0.0, -1.0, 0.0], normal=[0.0, 0.0, 1.0])
p0 = cq.Workplane(plane).polyline([[-0.4078816771507263, -0.5], [-0.4078816771507263, 0.5], [0.4078816771507263, 0.5], [0.4078816771507263, -0.5]]).close().extrude(0.944302499294281)
result = p0
