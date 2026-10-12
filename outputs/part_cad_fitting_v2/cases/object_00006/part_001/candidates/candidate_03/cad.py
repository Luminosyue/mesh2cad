import cadquery as cq
plane = cq.Plane(origin=[0.005570783264616242, 2.26417680143746, 0.9879939114094571], xDir=[1.0, 0.0, 0.0], normal=[0.0, 0.0, 1.0])
result = cq.Workplane(plane).sphere(2.4843782156910064)
