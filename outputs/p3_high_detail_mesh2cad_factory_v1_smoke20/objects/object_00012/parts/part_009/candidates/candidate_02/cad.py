import cadquery as cq
plane = cq.Plane(origin=[0.00037907642297143067, -0.5, 0.008534201695159225], xDir=[0.0, 0.0, 1.0], normal=[0.0, 1.0, 0.0])
result = cq.Workplane(plane).circle(0.021715208234859815).extrude(1.0)
