import cadquery as cq
plane = cq.Plane(origin=[0.0003679922762344271, 0.3989919919315723, -0.5], xDir=[0.0, -1.0, 0.0], normal=[0.0, 0.0, 1.0])
result = cq.Workplane(plane).circle(0.5150737512083592).extrude(1.0)
