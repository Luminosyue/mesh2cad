import cadquery as cq
plane = cq.Plane(origin=[-11778.235339428235, -0.5, 12060.857220909504], xDir=[0.0, 0.0, 1.0], normal=[0.0, 1.0, 0.0])
result = cq.Workplane(plane).circle(16857.802794976065).workplane(offset=1.0).circle(16857.968878420033).loft(ruled=True)
