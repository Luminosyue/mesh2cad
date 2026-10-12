import cadquery as cq
plane = cq.Plane(origin=[0.022985241500214606, -19.55960574949364, 0.17641642765922552], xDir=[1.0, 0.0, 0.0], normal=[0.0, 0.0, 1.0])
result = cq.Workplane(plane).sphere(19.572191182378997)
