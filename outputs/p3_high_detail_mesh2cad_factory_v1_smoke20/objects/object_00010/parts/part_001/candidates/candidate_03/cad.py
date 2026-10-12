import cadquery as cq
plane = cq.Plane(origin=[-0.0016367779612251748, -0.09449780732393265, 0.054029433476378896], xDir=[0.0, 0.0, 1.0], normal=[0.0, 1.0, 0.0])
result = cq.Workplane(plane).circle(0.37191889240082737).extrude(0.1889956146478653)
