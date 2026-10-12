import cadquery as cq
plane = cq.Plane(origin=[0.0027847300108793794, -1.3289062474035838, -0.4986632887768416], xDir=[1.0, 0.0, 0.0], normal=[0.0, 0.0, 1.0])
result = cq.Workplane(plane).sphere(1.4643033475702334)
