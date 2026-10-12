import cadquery as cq
plane = cq.Plane(origin=[0.012600063096583278, -0.4788952816593856, -0.0008608742162330551], xDir=[0.0, 0.0, 1.0], normal=[0.0, 1.0, 0.0])
result = cq.Workplane(plane).circle(np.float64(0.024644068797926053)).extrude(np.float64(1.0))
