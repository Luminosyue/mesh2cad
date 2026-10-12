import cadquery as cq
plane = cq.Plane(origin=[0.01246078193760502, -0.5, -0.0008134204573331582], xDir=[0.0, 0.0, 1.0], normal=[0.0, 1.0, 0.0])
result = cq.Workplane(plane).circle(0.024968596713760265).extrude(1.0)
