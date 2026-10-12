import cadquery as cq
plane = cq.Plane(origin=[-0.5095068913486933, -0.09430787988985355, 29.006898476809152], xDir=[1.0, 0.0, 0.0], normal=[0.0, 0.0, 1.0])
result = cq.Workplane(plane).sphere(29.028146784659544)
