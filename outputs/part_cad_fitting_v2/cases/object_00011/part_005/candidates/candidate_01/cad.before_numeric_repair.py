import cadquery as cq
plane = cq.Plane(origin=[-0.0009061122187218177, 0.00030809070428497714, -0.5208580157147071], xDir=[0.0, -1.0, 0.0], normal=[0.0, 0.0, 1.0])
result = cq.Workplane(plane).circle(np.float64(0.03790418301011335)).extrude(np.float64(1.0))
