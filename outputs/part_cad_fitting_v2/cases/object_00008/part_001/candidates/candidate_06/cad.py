import cadquery as cq
plane = cq.Plane(origin=[0.020290861429833048, 2.567539645735789, -0.43604913769547904], xDir=[1.0, 0.0, 0.0], normal=[0.0, 0.0, 1.0])
result = cq.Workplane(plane).sphere(2.6491296491092817)
