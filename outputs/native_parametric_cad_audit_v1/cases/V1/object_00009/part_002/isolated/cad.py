import cadquery as cq
plane = cq.Plane(origin=[-0.029937123721362466, 0.000995095679335518, -0.5], xDir=[0.0, -1.0, 0.0], normal=[0.0, 0.0, 1.0])
result = cq.Workplane(plane).circle(0.35329962356338523).extrude(1.0)
