import cadquery as cq
plane = cq.Plane(origin=[-0.014829220264854392, 0.023679891328352076, -0.07280822843313217], xDir=[0.0, -1.0, 0.0], normal=[0.0, 0.0, 1.0])
result = cq.Workplane(plane).circle(0.38525874227078105).extrude(0.14561645686626434)
