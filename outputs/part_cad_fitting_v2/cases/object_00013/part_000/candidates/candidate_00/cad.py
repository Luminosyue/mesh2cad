import cadquery as cq
plane = cq.Plane(origin=[-0.0006015941355137063, -0.5, 0.0005729089383637123], xDir=[0.0, 0.0, 1.0], normal=[0.0, 1.0, 0.0])
result = cq.Workplane(plane).circle(0.012739868894584078).extrude(1.0)
