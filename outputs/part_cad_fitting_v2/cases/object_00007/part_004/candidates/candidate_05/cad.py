import cadquery as cq
plane = cq.Plane(origin=[12190.235910069137, -0.5, 12807.057370345887], xDir=[0.0, 0.0, 1.0], normal=[0.0, 1.0, 0.0])
result = cq.Workplane(plane).circle(17681.088004666763).workplane(offset=1.0).circle(17681.095894103837).loft(ruled=True)
