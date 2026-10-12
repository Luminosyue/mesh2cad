import cadquery as cq
plane = cq.Plane(origin=[-0.5, 0.0004276692409736243, 0.010157331104531814], xDir=[0.0, 0.0, -1.0], normal=[1.0, 0.0, 0.0])
result = cq.Workplane(plane).circle(0.024263618340184312).workplane(offset=1.0).circle(0.024232137740002088).loft(ruled=True)
