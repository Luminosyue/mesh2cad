import cadquery as cq
plane = cq.Plane(origin=[-0.5, -0.0120747530988016, -0.01494024404579659], xDir=[0.0, 0.0, -1.0], normal=[1.0, 0.0, 0.0])
result = cq.Workplane(plane).circle(0.19757293520278668).extrude(1.0)
