import cadquery as cq
plane = cq.Plane(origin=[-0.007733001880432076, 0.0008982629617497031, -0.5], xDir=[0.0, -1.0, 0.0], normal=[0.0, 0.0, 1.0])
result = cq.Workplane(plane).circle(0.20123585859927132).extrude(1.0)
