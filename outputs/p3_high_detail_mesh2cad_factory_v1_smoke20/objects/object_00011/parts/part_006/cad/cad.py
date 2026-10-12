import cadquery as cq
plane = cq.Plane(origin=[0.014017509081255689, -0.00016996552889762177, -0.5], xDir=[0.0, -1.0, 0.0], normal=[0.0, 0.0, 1.0])
result = cq.Workplane(plane).circle(0.03584731376914921).extrude(1.0)
