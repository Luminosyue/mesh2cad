import cadquery as cq
plane = cq.Plane(origin=[-0.0005032799517169814, -0.00713809623398035, -0.5], xDir=[0.0, -1.0, 0.0], normal=[0.0, 0.0, 1.0])
result = cq.Workplane(plane).circle(0.036197224089559915).extrude(1.0)
