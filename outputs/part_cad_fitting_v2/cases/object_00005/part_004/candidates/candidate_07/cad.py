import cadquery as cq
plane = cq.Plane(origin=[-5.21897792859757, -320.5687070688014, -2.2032049316809035], xDir=[1.0, 0.0, 0.0], normal=[0.0, 0.0, 1.0])
result = cq.Workplane(plane).sphere(320.62036568671465)
