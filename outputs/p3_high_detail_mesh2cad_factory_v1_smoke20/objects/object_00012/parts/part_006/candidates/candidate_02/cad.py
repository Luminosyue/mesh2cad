import cadquery as cq
plane = cq.Plane(origin=[-0.00011838574871214647, 0.12197821645680272, -0.5], xDir=[0.0, -1.0, 0.0], normal=[0.0, 0.0, 1.0])
result = cq.Workplane(plane).circle(0.3063021321739743).extrude(1.0)
