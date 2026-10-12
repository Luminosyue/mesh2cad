import cadquery as cq
plane = cq.Plane(origin=[-0.014937805296672404, -0.03730106140702355, -0.28071962342975865], xDir=[0.0, -1.0, 0.0], normal=[0.0, 0.0, 1.0])
result = cq.Workplane(plane).circle(0.37257675897504033).extrude(0.6376765370368958)
