import cadquery as cq
plane = cq.Plane(origin=[0.011124226917335948, 7.333602011851372e-05, -0.5], xDir=[0.0, -1.0, 0.0], normal=[0.0, 0.0, 1.0])
result = cq.Workplane(plane).circle(0.03700861829212799).extrude(1.0)
