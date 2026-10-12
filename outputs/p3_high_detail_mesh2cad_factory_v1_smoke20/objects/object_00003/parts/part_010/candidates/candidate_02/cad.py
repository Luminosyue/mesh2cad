import cadquery as cq
plane = cq.Plane(origin=[-0.01141116391040295, -0.004602222489443771, -0.47017019987106323], xDir=[0.0, -1.0, 0.0], normal=[0.0, 0.0, 1.0])
result = cq.Workplane(plane).circle(0.5063766931142599).extrude(0.9403403997421265)
