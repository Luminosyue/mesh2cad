import cadquery as cq
plane = cq.Plane(origin=[-0.21216730773448944, 0.0, 0.0], xDir=[0.0, 0.0, -1.0], normal=[1.0, 0.0, 0.0])
result = cq.Workplane(plane).circle(0.4185912758111954).extrude(0.4243346154689789)
