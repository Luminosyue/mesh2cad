import cadquery as cq
plane = cq.Plane(origin=[0.004293568989798391, -0.017625891769135527, -0.5], xDir=[0.0, -1.0, 0.0], normal=[0.0, 0.0, 1.0])
result = cq.Workplane(plane).circle(0.3241727012792676).workplane(offset=1.0).circle(0.24109334825769166).loft(ruled=True)
