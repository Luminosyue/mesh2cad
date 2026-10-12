import cadquery as cq
plane = cq.Plane(origin=[-0.1840490698814392, 0.004126402927467104, 9.936030155315917], xDir=[0.0, 0.0, -1.0], normal=[1.0, 0.0, 0.0])
result = cq.Workplane(plane).circle(9.940110621511888).extrude(0.3680981397628784)
