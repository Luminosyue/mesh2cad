import cadquery as cq
plane = cq.Plane(origin=[-0.004100732176826164, -0.5, 0.0035725275923304285], xDir=[0.0, 0.0, 1.0], normal=[0.0, 1.0, 0.0])
result = cq.Workplane(plane).circle(0.04499433583733206).extrude(1.0)
