import cadquery as cq
plane = cq.Plane(origin=[0.014109220907483629, -0.0001341272151248869, -0.5422236088842061], xDir=[0.0, -1.0, 0.0], normal=[0.0, 0.0, 1.0])
result = cq.Workplane(plane).circle(np.float64(0.03584731376914921)).extrude(np.float64(1.0))
