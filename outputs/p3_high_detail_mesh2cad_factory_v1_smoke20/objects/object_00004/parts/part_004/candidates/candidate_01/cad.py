import cadquery as cq
plane = cq.Plane(origin=[-0.30838584899902344, 0.0010672494555405143, -0.006610047401663054], xDir=[0.0, 0.0, -1.0], normal=[1.0, 0.0, 0.0])
result = cq.Workplane(plane).circle(0.45681475972274826).extrude(0.6167716979980469)
