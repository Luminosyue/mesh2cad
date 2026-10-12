import cadquery as cq
plane = cq.Plane(origin=[-0.27110136122027284, -16.988127092997537, -0.18523757904496008], xDir=[1.0, 0.0, 0.0], normal=[0.0, 0.0, 1.0])
result = cq.Workplane(plane).sphere(17.040081210334584)
