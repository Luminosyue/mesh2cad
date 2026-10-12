import cadquery as cq
plane = cq.Plane(origin=[0.006793165476454906, 0.8352740724878258, 0.005248122077925958], xDir=[1.0, 0.0, 0.0], normal=[0.0, 0.0, 1.0])
result = cq.Workplane(plane).sphere(0.948949315599374)
