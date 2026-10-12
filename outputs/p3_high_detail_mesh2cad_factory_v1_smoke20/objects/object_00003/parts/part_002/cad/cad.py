import cadquery as cq
plane = cq.Plane(origin=[-0.006438302940838997, 0.027793938264993906, -0.36485812067985535], xDir=[0.0, -1.0, 0.0], normal=[0.0, 0.0, 1.0])
result = cq.Workplane(plane).circle(0.4254506605305641).extrude(0.7297162413597107)
