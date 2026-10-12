import cadquery as cq
plane = cq.Plane(origin=[-0.5, 0.026575082086710583, 0.0642204387483388], xDir=[0.0, 0.0, -1.0], normal=[1.0, 0.0, 0.0])
result = cq.Workplane(plane).circle(0.1104334949189484).extrude(1.0)
