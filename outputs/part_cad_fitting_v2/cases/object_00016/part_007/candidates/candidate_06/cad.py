import cadquery as cq
plane = cq.Plane(origin=[2395.2133532357034, 0.7645067450099281, -3.6078875071526095], xDir=[1.0, 0.0, 0.0], normal=[0.0, 0.0, 1.0])
result = cq.Workplane(plane).sphere(2395.2135150982185)
