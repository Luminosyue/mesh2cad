import cadquery as cq
plane = cq.Plane(origin=[-0.0035909331735903965, -0.03902602940797806, 0.003338258706530324], xDir=[0.0, 0.0, 1.0], normal=[0.0, 1.0, 0.0])
result = cq.Workplane(plane).circle(0.29356453062451004).extrude(0.07805205881595612)
