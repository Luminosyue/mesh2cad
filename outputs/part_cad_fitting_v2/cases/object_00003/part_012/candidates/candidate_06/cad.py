import cadquery as cq
plane = cq.Plane(origin=[-0.0017602408715589421, -1.0087847782761727, -0.2252450993700029], xDir=[1.0, 0.0, 0.0], normal=[0.0, 0.0, 1.0])
result = cq.Workplane(plane).sphere(1.1364668656781316)
