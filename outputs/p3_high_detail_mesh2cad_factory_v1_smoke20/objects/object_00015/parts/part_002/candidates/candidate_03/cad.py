import cadquery as cq
plane = cq.Plane(origin=[0.004093133098995502, -0.5, 0.005509458456543347], xDir=[0.0, 0.0, 1.0], normal=[0.0, 1.0, 0.0])
result = cq.Workplane(plane).circle(0.045534333973663056).extrude(1.0)
