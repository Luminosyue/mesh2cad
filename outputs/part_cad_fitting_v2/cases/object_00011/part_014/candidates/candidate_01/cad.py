import cadquery as cq
plane = cq.Plane(origin=[-0.00040643737871601195, 0.0002486371193571897, -0.5127577739937221], xDir=[0.0, -1.0, 0.0], normal=[0.0, 0.0, 1.0])
result = cq.Workplane(plane).circle(0.0384620210505544).extrude(1.0)
