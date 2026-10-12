import cadquery as cq
plane = cq.Plane(origin=[-3.3058971443249483, 0.0460235687205252, 0.07717874457429662], xDir=[1.0, 0.0, 0.0], normal=[0.0, 0.0, 1.0])
result = cq.Workplane(plane).sphere(3.366314400281132)
