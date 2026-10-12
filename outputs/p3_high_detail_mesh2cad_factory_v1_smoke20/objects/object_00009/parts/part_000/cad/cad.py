import cadquery as cq
plane = cq.Plane(origin=[0.0049916424936549166, -0.0011724562128991353, -0.5], xDir=[0.0, -1.0, 0.0], normal=[0.0, 0.0, 1.0])
result = cq.Workplane(plane).circle(0.19719969416687286).extrude(1.0)
