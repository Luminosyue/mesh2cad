import cadquery as cq
plane = cq.Plane(origin=[0.0008364671064170448, -0.5, 0.008769840961603204], xDir=[0.0, 0.0, 1.0], normal=[0.0, 1.0, 0.0])
result = cq.Workplane(plane).circle(0.021863357290638624).extrude(1.0)
