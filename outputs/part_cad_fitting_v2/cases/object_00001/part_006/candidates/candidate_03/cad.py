import cadquery as cq
plane = cq.Plane(origin=[-0.08181679571372734, 0.2119008468942374, -2.741894244134188], xDir=[1.0, 0.0, 0.0], normal=[0.0, 0.0, 1.0])
result = cq.Workplane(plane).sphere(2.778486371446771)
