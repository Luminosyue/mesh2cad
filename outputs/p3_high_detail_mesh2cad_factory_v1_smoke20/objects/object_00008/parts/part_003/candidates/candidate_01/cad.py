import cadquery as cq
plane = cq.Plane(origin=[-0.0030832863407906363, -0.0016657424362771004, -0.08144080638885498], xDir=[0.0, -1.0, 0.0], normal=[0.0, 0.0, 1.0])
result = cq.Workplane(plane).circle(0.3555675543726537).extrude(0.16288161277770996)
