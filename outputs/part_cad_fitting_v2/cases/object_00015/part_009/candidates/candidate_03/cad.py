import cadquery as cq
plane = cq.Plane(origin=[1.8084692092189754, 12.025290612760664, 0.10549967192405105], xDir=[1.0, 0.0, 0.0], normal=[0.0, 0.0, 1.0])
result = cq.Workplane(plane).sphere(12.197154235833564)
