import cadquery as cq
plane = cq.Plane(origin=[0.059478327651476565, 0.0007951634911506343, -0.58], xDir=[0.0, -1.0, 0.0], normal=[0.0, 0.0, 1.0])
result = cq.Workplane(plane).circle(np.float64(0.35110240446132585)).extrude(np.float64(1.0))
