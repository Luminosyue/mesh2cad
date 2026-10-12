import cadquery as cq
plane = cq.Plane(origin=[1.1455592140371866, 0.10283500967393137, -1.56952325657478], xDir=[1.0, 0.0, 0.0], normal=[0.0, 0.0, 1.0])
result = cq.Workplane(plane).sphere(2.0083867104870796)
