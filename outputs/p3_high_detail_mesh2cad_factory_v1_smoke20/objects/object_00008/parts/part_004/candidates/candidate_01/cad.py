import cadquery as cq
plane = cq.Plane(origin=[-0.06933746486902237, 0.009045803937226427, -0.03891459252457743], xDir=[0.0, 0.0, -1.0], normal=[1.0, 0.0, 0.0])
result = cq.Workplane(plane).circle(0.2914247825864211).extrude(0.13867492973804474)
