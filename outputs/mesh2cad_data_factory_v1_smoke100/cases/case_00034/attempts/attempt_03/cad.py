import cadquery as cq
plane = cq.Plane(origin=[-0.03516247123479843, 0.0, 0.0], xDir=[0.0, 0.0, -1.0], normal=[1.0, 0.0, 0.0])
result = cq.Workplane(plane).circle(0.4450141340494156).extrude(0.07032494246959686)
