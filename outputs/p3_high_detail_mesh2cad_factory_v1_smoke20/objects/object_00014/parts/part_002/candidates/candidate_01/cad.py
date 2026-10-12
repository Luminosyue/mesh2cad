import cadquery as cq
plane = cq.Plane(origin=[0.000412870571291607, -0.5, -0.0017738636745492223], xDir=[0.0, 0.0, 1.0], normal=[0.0, 1.0, 0.0])
result = cq.Workplane(plane).circle(0.3701673850212681).extrude(1.0)
