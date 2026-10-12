import cadquery as cq
plane = cq.Plane(origin=[0.00533413697280647, 0.00018839471448732454, -0.5207383739886583], xDir=[0.0, -1.0, 0.0], normal=[0.0, 0.0, 1.0])
result = cq.Workplane(plane).circle(np.float64(0.0377353397030449)).extrude(np.float64(1.0))
