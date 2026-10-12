import cadquery as cq
plane = cq.Plane(origin=[-0.49942679245935945, -0.01595381022555642, 0.07013576123716397], xDir=[0.0, 0.0, -1.0], normal=[1.0, 0.0, 0.0])
result = cq.Workplane(plane).circle(np.float64(0.1104334949189484)).extrude(np.float64(1.0))
