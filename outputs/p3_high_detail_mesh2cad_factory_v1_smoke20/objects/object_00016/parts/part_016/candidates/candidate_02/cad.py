import cadquery as cq
plane = cq.Plane(origin=[-0.010291446614901074, -0.5, -0.005030123198446958], xDir=[0.0, 0.0, 1.0], normal=[0.0, 1.0, 0.0])
result = cq.Workplane(plane).circle(0.03521052864317354).extrude(1.0)
