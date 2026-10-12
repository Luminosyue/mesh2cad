import cadquery as cq
plane = cq.Plane(origin=[0.0, 0.0, -0.04054071754217148], xDir=[0.0, -1.0, 0.0], normal=[0.0, 0.0, 1.0])
p0 = cq.Workplane(plane).polyline([[-0.5, -0.3028501272201538], [-0.5, 0.3028501272201538], [0.5, 0.3028501272201538], [0.5, -0.3028501272201538]]).close().extrude(0.08108143508434296)
result = p0
