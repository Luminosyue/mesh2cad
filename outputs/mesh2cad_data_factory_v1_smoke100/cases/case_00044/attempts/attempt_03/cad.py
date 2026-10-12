import cadquery as cq
plane = cq.Plane(origin=[-0.1720106601715088, 0.0, 0.0], xDir=[0.0, 0.0, -1.0], normal=[1.0, 0.0, 0.0])
result = cq.Workplane(plane).circle(0.43804165720939636).extrude(0.3440213203430176)
