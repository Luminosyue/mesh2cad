import cadquery as cq
plane = cq.Plane(origin=[0.0, 0.0, -0.38030269742012024], xDir=[0.0, -1.0, 0.0], normal=[0.0, 0.0, 1.0])
result = cq.Workplane(plane).circle(0.4710676223039627).extrude(0.7606053948402405)
