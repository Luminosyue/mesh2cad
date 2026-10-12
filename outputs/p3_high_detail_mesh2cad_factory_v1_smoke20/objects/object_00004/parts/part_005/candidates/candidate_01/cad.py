import cadquery as cq
plane = cq.Plane(origin=[-0.0029812684993926752, 0.008301278319873602, -0.5], xDir=[0.0, -1.0, 0.0], normal=[0.0, 0.0, 1.0])
result = cq.Workplane(plane).circle(0.4256917519741106).extrude(1.0)
