import cadquery as cq
plane = cq.Plane(origin=[-0.23278488218784332, 0.0, 0.0], xDir=[0.0, 0.0, -1.0], normal=[1.0, 0.0, 0.0])
result = cq.Workplane(plane).circle(0.4947999268770218).extrude(0.46556976437568665)
