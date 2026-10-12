import cadquery as cq
plane = cq.Plane(origin=[0.00020857419579650672, -0.014233863034953439, -0.5323107253074782], xDir=[0.0, -1.0, 0.0], normal=[0.0, 0.0, 1.0])
result = cq.Workplane(plane).circle(np.float64(0.03602712582839516)).extrude(np.float64(1.0))
