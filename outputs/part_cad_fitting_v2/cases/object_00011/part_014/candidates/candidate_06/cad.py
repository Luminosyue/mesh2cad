import cadquery as cq
plane = cq.Plane(origin=[-0.0004064373834912876, 0.00024863712639387964, -0.49556048212250536], xDir=[0.0, -1.0, 0.0], normal=[0.0, 0.0, 1.0])
result = cq.Workplane(plane).circle(0.03983202704022013).extrude(0.9656054162575665)
