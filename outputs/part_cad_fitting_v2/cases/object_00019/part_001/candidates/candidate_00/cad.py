import cadquery as cq
plane = cq.Plane(origin=[-0.5, -0.15779837401587557, 0.004251010440702655], xDir=[0.0, 0.0, -1.0], normal=[1.0, 0.0, 0.0])
result = cq.Workplane(plane).circle(0.16801052035525893).extrude(1.0)
