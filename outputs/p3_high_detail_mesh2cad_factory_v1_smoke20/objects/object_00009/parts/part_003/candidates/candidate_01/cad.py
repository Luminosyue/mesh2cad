import cadquery as cq
plane = cq.Plane(origin=[-0.0029506121882010017, -0.13941098749637604, -0.022685975871434845], xDir=[0.0, 0.0, 1.0], normal=[0.0, 1.0, 0.0])
result = cq.Workplane(plane).circle(0.39822609473405635).extrude(0.2788219749927521)
