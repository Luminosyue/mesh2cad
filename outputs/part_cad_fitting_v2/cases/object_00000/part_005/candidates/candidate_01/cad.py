import cadquery as cq
plane = cq.Plane(origin=[0.0035781982431624666, -0.02574375714365055, -0.054704944284449164], xDir=[0.0, -1.0, 0.0], normal=[0.0, 0.0, 1.0])
result = cq.Workplane(plane).box(1.0, 0.6536282896995544, 0.22376663982868195)
