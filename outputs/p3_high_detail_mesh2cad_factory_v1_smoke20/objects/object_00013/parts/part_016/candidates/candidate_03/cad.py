import cadquery as cq
plane = cq.Plane(origin=[-0.0009019468687869047, 0.0037172675954121916, -0.5], xDir=[0.0, -1.0, 0.0], normal=[0.0, 0.0, 1.0])
result = cq.Workplane(plane).circle(0.055109970938903505).extrude(1.0)
