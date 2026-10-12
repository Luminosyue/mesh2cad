import cadquery as cq
plane = cq.Plane(origin=[-0.09789593344298803, 0.1880557571774189, -0.09510517865419388], xDir=[0.0, -1.0, 0.0], normal=[0.0, 0.0, 1.0])
result = cq.Workplane(plane).circle(0.578762392093096).extrude(0.19021035730838776)
