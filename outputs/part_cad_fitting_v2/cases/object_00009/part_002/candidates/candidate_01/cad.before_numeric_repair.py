import cadquery as cq
plane = cq.Plane(origin=[-0.018227054111023353, -0.0016853232483130028, -0.58], xDir=[0.0, -1.0, 0.0], normal=[0.0, 0.0, 1.0])
result = cq.Workplane(plane).circle(np.float64(0.35329962356338523)).extrude(np.float64(1.0))
