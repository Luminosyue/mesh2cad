import cadquery as cq
plane = cq.Plane(origin=[-0.030921392486851343, -0.5, 0.6740452701734547], xDir=[0.0, 0.0, 1.0], normal=[0.0, 1.0, 0.0])
result = cq.Workplane(plane).circle(0.7040479592531304).extrude(1.0)
