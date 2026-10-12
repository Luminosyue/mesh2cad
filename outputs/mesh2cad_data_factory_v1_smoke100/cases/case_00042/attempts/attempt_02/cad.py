import cadquery as cq
plane = cq.Plane(origin=[0.0, -0.01998845674097538, 0.0], xDir=[0.0, 0.0, 1.0], normal=[0.0, 1.0, 0.0])
result = cq.Workplane(plane).circle(0.4571067541837692).extrude(0.03997691348195076)
