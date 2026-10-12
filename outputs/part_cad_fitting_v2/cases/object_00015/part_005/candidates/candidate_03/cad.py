import cadquery as cq
plane = cq.Plane(origin=[0.026809087455013866, -5.776505277991798, 2.360710839067061], xDir=[1.0, 0.0, 0.0], normal=[0.0, 0.0, 1.0])
result = cq.Workplane(plane).sphere(6.252442279698035)
