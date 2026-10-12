import cadquery as cq
plane = cq.Plane(origin=[-0.0005712994783639616, 0.00049882029380481, -0.5], xDir=[0.0, -1.0, 0.0], normal=[0.0, 0.0, 1.0])
result = cq.Workplane(plane).circle(0.0384620210505544).extrude(1.0)
