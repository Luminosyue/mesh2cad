import cadquery as cq
plane = cq.Plane(origin=[-0.013199223690379479, -0.014436011748506315, -0.5], xDir=[0.0, -1.0, 0.0], normal=[0.0, 0.0, 1.0])
result = cq.Workplane(plane).circle(0.26108573609890107).extrude(1.0)
