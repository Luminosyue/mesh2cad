import cadquery as cq
plane = cq.Plane(origin=[0.029716723045573566, -0.5, 0.02517594016251781], xDir=[0.0, 0.0, 1.0], normal=[0.0, 1.0, 0.0])
result = cq.Workplane(plane).circle(0.28795433265109377).extrude(1.0)
