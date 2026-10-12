import cadquery as cq
plane = cq.Plane(origin=[0.07356406815079033, -0.03275025381495664, -0.1274489408773946], xDir=[1.0, 0.0, 0.0], normal=[0.0, 0.0, 1.0])
result = cq.Workplane(plane).sphere(0.38595460803622456)
