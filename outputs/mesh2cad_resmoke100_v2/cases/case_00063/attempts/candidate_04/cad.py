import cadquery as cq
plane = cq.Plane(origin=[0.0, -0.4983421266078949, 0.0], xDir=[0.0, 0.0, 1.0], normal=[0.0, 1.0, 0.0])
p0 = cq.Workplane(plane).polyline([[0.5, -0.0676388293504715], [-0.5, -0.0676388293504715], [-0.5, 0.0676388293504715], [0.5, 0.0676388293504715]]).close().extrude(0.9966842532157898)
result = p0
