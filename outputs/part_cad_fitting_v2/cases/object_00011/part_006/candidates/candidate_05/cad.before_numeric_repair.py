import cadquery as cq
plane = cq.Plane(origin=[0.01410922088285567, -0.0001341272440496898, -0.5250263170129893], xDir=[0.0, -1.0, 0.0], normal=[0.0, 0.0, 1.0])
result = cq.Workplane(plane).circle(np.float64(0.034614360333774914)).extrude(np.float64(0.9656054162575665))
