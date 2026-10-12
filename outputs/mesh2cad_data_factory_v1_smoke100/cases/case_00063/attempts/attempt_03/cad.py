import cadquery as cq
plane = cq.Plane(origin=[-0.0676388293504715, 0.0, 0.0], xDir=[0.0, 0.0, -1.0], normal=[1.0, 0.0, 0.0])
result = cq.Workplane(plane).circle(0.49917106330394745).extrude(0.135277658700943)
