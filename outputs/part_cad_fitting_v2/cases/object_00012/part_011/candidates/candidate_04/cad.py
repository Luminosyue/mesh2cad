import cadquery as cq
plane = cq.Plane(origin=[-0.006573360232157616, -0.5, 0.000599064492744962], xDir=[0.0, 0.0, 1.0], normal=[0.0, 1.0, 0.0])
result = cq.Workplane(plane).circle(0.024336494708042656).extrude(1.0)
