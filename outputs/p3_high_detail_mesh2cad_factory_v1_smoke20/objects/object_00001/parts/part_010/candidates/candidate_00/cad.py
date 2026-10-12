import cadquery as cq
plane = cq.Plane(origin=[0.01949823208588744, -0.12833465727928128, -0.09939397871494293], xDir=[0.0, -1.0, 0.0], normal=[0.0, 0.0, 1.0])
result = cq.Workplane(plane).circle(0.46303535832997494).extrude(0.19878795742988586)
