import cadquery as cq
plane = cq.Plane(origin=[-0.009208246684092232, -0.5, -0.12748591717676694], xDir=[0.0, 0.0, 1.0], normal=[0.0, 1.0, 0.0])
result = cq.Workplane(plane).circle(0.5499470421638686).workplane(offset=1.0).circle(0.5349672013662641).loft(ruled=True)
