import cadquery as cq
plane = cq.Plane(origin=[-0.30728480404236647, -0.1724137057842056, -1.0264622641295542], xDir=[1.0, 0.0, 0.0], normal=[0.0, 0.0, 1.0])
result = cq.Workplane(plane).sphere(1.169145684298998)
