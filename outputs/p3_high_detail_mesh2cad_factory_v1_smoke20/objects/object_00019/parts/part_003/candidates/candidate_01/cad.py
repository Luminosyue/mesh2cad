import cadquery as cq
plane = cq.Plane(origin=[-0.5, -0.014763108999183025, 0.00013971509421172412], xDir=[0.0, 0.0, -1.0], normal=[1.0, 0.0, 0.0])
result = cq.Workplane(plane).circle(0.053415534349436244).extrude(1.0)
