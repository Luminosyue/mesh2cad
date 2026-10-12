import cadquery as cq
plane = cq.Plane(origin=[-0.0008350722125829677, -0.5, 0.013357533809785946], xDir=[0.0, 0.0, 1.0], normal=[0.0, 1.0, 0.0])
result = cq.Workplane(plane).circle(0.02540358946559969).extrude(1.0)
