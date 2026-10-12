import cadquery as cq
plane = cq.Plane(origin=[0.006439607498716272, 3.222566952375223e-05, -0.5], xDir=[0.0, -1.0, 0.0], normal=[0.0, 0.0, 1.0])
result = cq.Workplane(plane).circle(0.03717042328437483).extrude(1.0)
