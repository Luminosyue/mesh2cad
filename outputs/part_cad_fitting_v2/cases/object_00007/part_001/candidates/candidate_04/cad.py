import cadquery as cq
plane = cq.Plane(origin=[-0.5, 0.1797520652408882, -0.027496978960890497], xDir=[0.0, 0.0, -1.0], normal=[1.0, 0.0, 0.0])
result = cq.Workplane(plane).circle(0.22880279655799782).extrude(1.0)
