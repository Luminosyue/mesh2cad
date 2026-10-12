import cadquery as cq
plane = cq.Plane(origin=[80.02545098689626, -1574.074698973701, 1460.4038126876665], xDir=[1.0, 0.0, 0.0], normal=[0.0, 0.0, 1.0])
result = cq.Workplane(plane).sphere(2148.743255634228)
