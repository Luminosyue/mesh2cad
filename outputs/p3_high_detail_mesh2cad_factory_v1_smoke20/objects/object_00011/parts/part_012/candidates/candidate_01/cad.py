import cadquery as cq
plane = cq.Plane(origin=[-0.00421157437569308, 0.0002621385580780401, -0.5], xDir=[0.0, -1.0, 0.0], normal=[0.0, 0.0, 1.0])
result = cq.Workplane(plane).circle(0.03711168516388972).extrude(1.0)
