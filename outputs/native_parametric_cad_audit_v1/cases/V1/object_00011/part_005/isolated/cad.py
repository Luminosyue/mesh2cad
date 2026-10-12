import cadquery as cq
plane = cq.Plane(origin=[-0.0005860987550958901, 0.0005226752662095492, -0.5], xDir=[0.0, -1.0, 0.0], normal=[0.0, 0.0, 1.0])
result = cq.Workplane(plane).circle(0.03790418301011335).extrude(1.0)
