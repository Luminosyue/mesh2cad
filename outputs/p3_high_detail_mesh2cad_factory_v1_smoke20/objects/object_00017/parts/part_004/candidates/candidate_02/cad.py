import cadquery as cq
plane = cq.Plane(origin=[-0.5, -0.02827656384810942, 0.34419437494425364], xDir=[0.0, 0.0, -1.0], normal=[1.0, 0.0, 0.0])
result = cq.Workplane(plane).circle(0.41953910304573755).extrude(1.0)
