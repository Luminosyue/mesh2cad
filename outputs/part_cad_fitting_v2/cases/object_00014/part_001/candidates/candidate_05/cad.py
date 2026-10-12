import cadquery as cq
plane = cq.Plane(origin=[0.4617912759795849, 0.16415459279395478, -0.5], xDir=[0.0, -1.0, 0.0], normal=[0.0, 0.0, 1.0])
result = cq.Workplane(plane).circle(0.6491855399224409).workplane(offset=1.0).circle(0.6600999923380602).loft(ruled=True)
