import cadquery as cq
plane = cq.Plane(origin=[-0.018500719777689897, -0.09280088914420037, -0.2976777255535126], xDir=[0.0, -1.0, 0.0], normal=[0.0, 0.0, 1.0])
result = cq.Workplane(plane).circle(0.4909964164657217).workplane(offset=0.5953554511070251).circle(0.3351293644643333).loft(ruled=True)
