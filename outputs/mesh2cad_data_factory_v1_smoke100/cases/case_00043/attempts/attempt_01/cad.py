import cadquery as cq
plane = cq.Plane(origin=[0.0, -0.34746184945106506, 0.0], xDir=[0.0, 0.0, 1.0], normal=[0.0, 1.0, 0.0])
p0 = cq.Workplane(plane).polyline([[0.5, -0.3912437856197357], [-0.5, -0.3912437856197357], [-0.5, 0.3912437856197357], [0.5, 0.3912437856197357]]).close().extrude(0.6949236989021301)
result = p0
