import cadquery as cq
plane = cq.Plane(origin=[-3.90849554859074e-05, 0.12474849421639643, -0.5], xDir=[0.0, -1.0, 0.0], normal=[0.0, 0.0, 1.0])
result = cq.Workplane(plane).circle(0.30156896062480854).extrude(1.0)
