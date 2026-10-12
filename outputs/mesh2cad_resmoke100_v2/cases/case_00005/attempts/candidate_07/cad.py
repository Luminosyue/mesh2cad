import cadquery as cq
plane = cq.Plane(origin=[0.026096450920806525, -0.025864876044191888, 0.00844996418247129], xDir=[1.0, 0.0, 0.0], normal=[0.0, 0.0, 1.0])
result = cq.Workplane(plane).sphere(0.35909058115795317)
