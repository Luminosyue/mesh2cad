import cadquery as cq
plane = cq.Plane(origin=[-0.0009015512736645495, 2.583990406232387e-05, -0.5], xDir=[0.0, -1.0, 0.0], normal=[0.0, 0.0, 1.0])
result = cq.Workplane(plane).circle(0.03783457197312404).extrude(1.0)
