import cadquery as cq
plane = cq.Plane(origin=[-9.390435272056208e-05, -0.002209101850725552, -0.5], xDir=[0.0, -1.0, 0.0], normal=[0.0, 0.0, 1.0])
result = cq.Workplane(plane).circle(0.03493482445470891).extrude(1.0)
