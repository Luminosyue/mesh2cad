import cadquery as cq
plane = cq.Plane(origin=[-0.0003975492543009723, -0.008817510683668268, -0.5], xDir=[0.0, -1.0, 0.0], normal=[0.0, 0.0, 1.0])
result = cq.Workplane(plane).circle(0.03454873183687689).extrude(1.0)
