import cadquery as cq
plane = cq.Plane(origin=[-0.354434996843338, 2.0632691539496117, 0.0006863860120935493], xDir=[0.0, 0.0, -1.0], normal=[1.0, 0.0, 0.0])
result = cq.Workplane(plane).circle(2.151138695965626).extrude(0.708869993686676)
