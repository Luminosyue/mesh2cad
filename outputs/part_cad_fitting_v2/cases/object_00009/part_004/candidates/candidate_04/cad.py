import cadquery as cq
plane = cq.Plane(origin=[0.08152555646510116, 0.0026360278746773214, -0.5], xDir=[0.0, -1.0, 0.0], normal=[0.0, 0.0, 1.0])
result = cq.Workplane(plane).circle(0.3519306647347099).extrude(1.0)
