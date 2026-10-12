import cadquery as cq
plane = cq.Plane(origin=[-0.09789593344298803, 0.1880557571774189, -0.09510517865419388], xDir=[0.0, -1.0, 0.0], normal=[0.0, 0.0, 1.0])
result = cq.Workplane(plane).circle(0.590820669079393).workplane(offset=0.19021035730838776).circle(0.5560596989567915).loft(ruled=True)
