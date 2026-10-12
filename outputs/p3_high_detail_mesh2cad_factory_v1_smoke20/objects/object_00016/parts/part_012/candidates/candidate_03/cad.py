import cadquery as cq
plane = cq.Plane(origin=[0.37282448984404165, -0.5, -0.010243063974123721], xDir=[0.0, 0.0, 1.0], normal=[0.0, 1.0, 0.0])
result = cq.Workplane(plane).circle(0.39432844869202865).extrude(1.0)
