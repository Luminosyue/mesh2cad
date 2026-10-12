import cadquery as cq
plane = cq.Plane(origin=[-0.009908216066337933, -0.04722492396865827, -0.3188382685184479], xDir=[0.0, -1.0, 0.0], normal=[0.0, 0.0, 1.0])
result = cq.Workplane(plane).circle(0.37257675897504033).extrude(0.6376765370368958)
