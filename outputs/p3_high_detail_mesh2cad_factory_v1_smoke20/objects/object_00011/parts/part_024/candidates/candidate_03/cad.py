import cadquery as cq
plane = cq.Plane(origin=[0.007094727769568631, -0.5, -0.01021113990106779], xDir=[0.0, 0.0, 1.0], normal=[0.0, 1.0, 0.0])
result = cq.Workplane(plane).circle(0.04164554077874217).extrude(1.0)
