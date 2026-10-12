import cadquery as cq
plane = cq.Plane(origin=[-0.0194386101568432, -0.037266253395901575, -0.42], xDir=[0.0, -1.0, 0.0], normal=[0.0, 0.0, 1.0])
result = cq.Workplane(plane).circle(np.float64(0.2693547205493011)).extrude(np.float64(1.0))
