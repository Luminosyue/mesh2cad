import cadquery as cq
plane = cq.Plane(origin=[-0.03675639964847487, 0.001616353015876906, -0.5], xDir=[0.0, -1.0, 0.0], normal=[0.0, 0.0, 1.0])
result = cq.Workplane(plane).circle(0.35524357520240873).extrude(1.0)
