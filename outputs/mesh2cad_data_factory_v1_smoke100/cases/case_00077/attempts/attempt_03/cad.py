import cadquery as cq
plane = cq.Plane(origin=[0.0, -0.11661313474178314, 0.0], xDir=[0.0, 0.0, 1.0], normal=[0.0, 1.0, 0.0])
result = cq.Workplane(plane).circle(0.39195725321769714).extrude(0.23322626948356628)
