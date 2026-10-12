import cadquery as cq
plane = cq.Plane(origin=[0.006312730316063544, 3.2148002898617155e-05, -0.5265646786885217], xDir=[0.0, -1.0, 0.0], normal=[0.0, 0.0, 1.0])
result = cq.Workplane(plane).circle(np.float64(0.037208345699049045)).extrude(np.float64(1.0))
