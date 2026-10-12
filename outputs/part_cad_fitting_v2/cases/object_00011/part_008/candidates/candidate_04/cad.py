import cadquery as cq
plane = cq.Plane(origin=[-0.008982935789829026, 3.392640803019045e-05, -0.5], xDir=[0.0, -1.0, 0.0], normal=[0.0, 0.0, 1.0])
result = cq.Workplane(plane).circle(0.036250383784434285).extrude(1.0)
