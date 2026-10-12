import cadquery as cq
plane = cq.Plane(origin=[0.0013498277432141045, -0.5, -0.0013010838082505468], xDir=[0.0, 0.0, 1.0], normal=[0.0, 1.0, 0.0])
result = cq.Workplane(plane).circle(0.011983886384736355).extrude(1.0)
