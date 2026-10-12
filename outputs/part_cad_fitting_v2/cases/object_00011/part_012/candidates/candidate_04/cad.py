import cadquery as cq
plane = cq.Plane(origin=[-0.004657961507024726, -1.824343125595246e-05, -0.5], xDir=[0.0, -1.0, 0.0], normal=[0.0, 0.0, 1.0])
result = cq.Workplane(plane).circle(0.03701365084100032).extrude(1.0)
