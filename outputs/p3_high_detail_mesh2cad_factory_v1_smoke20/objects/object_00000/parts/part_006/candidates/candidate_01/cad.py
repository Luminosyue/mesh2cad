import cadquery as cq
plane = cq.Plane(origin=[-0.0009095763077397873, -0.5, 0.16543722930157723], xDir=[0.0, 0.0, 1.0], normal=[0.0, 1.0, 0.0])
result = cq.Workplane(plane).circle(0.3217638247955285).extrude(1.0)
