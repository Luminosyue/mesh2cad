import cadquery as cq
plane = cq.Plane(origin=[0.0, 0.0, 0.0], xDir=[0.0, -1.0, 0.0], normal=[0.0, 0.0, 1.0])
result = cq.Workplane(plane).box(0.12186051905155182,0.09434251487255096,1.0)
