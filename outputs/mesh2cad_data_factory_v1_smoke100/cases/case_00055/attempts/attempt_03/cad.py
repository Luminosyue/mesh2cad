import cadquery as cq
plane = cq.Plane(origin=[0.0, -0.005235642660409212, 0.0], xDir=[0.0, 0.0, 1.0], normal=[0.0, 1.0, 0.0])
result = cq.Workplane(plane).circle(0.3610384538769722).extrude(0.010471285320818424)
