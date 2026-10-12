import cadquery as cq
plane = cq.Plane(origin=[0.0, 0.0, -0.3081547021865845], xDir=[0.0, -1.0, 0.0], normal=[0.0, 0.0, 1.0])
result = cq.Workplane(plane).circle(0.3402002155780792).extrude(0.616309404373169)
