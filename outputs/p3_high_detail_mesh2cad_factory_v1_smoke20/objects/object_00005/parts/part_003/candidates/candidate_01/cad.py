import cadquery as cq
plane = cq.Plane(origin=[-0.25221335887908936, 1.0600142518326654, 0.026852025686399692], xDir=[0.0, 0.0, -1.0], normal=[1.0, 0.0, 0.0])
result = cq.Workplane(plane).circle(1.0951614710319315).extrude(0.5044267177581787)
