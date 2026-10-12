import cadquery as cq
plane = cq.Plane(origin=[0.0029384218582228045, 0.007236571896549151, 0.05814169760248857], xDir=[1.0, 0.0, 0.0], normal=[0.0, 0.0, 1.0])
result = cq.Workplane(plane).sphere(0.4682321014070741)
