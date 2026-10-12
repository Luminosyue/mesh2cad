import cadquery as cq
plane = cq.Plane(origin=[-0.018500719777689897, -0.09280088914420037, -0.2976777255535126], xDir=[0.0, -1.0, 0.0], normal=[0.0, 0.0, 1.0])
result = cq.Workplane(plane).circle(0.3878505236553353).extrude(0.5953554511070251)
