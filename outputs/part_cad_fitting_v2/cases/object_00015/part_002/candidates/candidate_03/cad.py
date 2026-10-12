import cadquery as cq
plane = cq.Plane(origin=[-0.0621362142264843, 0.0740411006080404, 2.256869512200396], xDir=[0.0, 0.0, -1.0], normal=[1.0, 0.0, 0.0])
result = cq.Workplane(plane).circle(2.281597284991642).extrude(0.1242724284529686)
