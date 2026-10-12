import cadquery as cq
plane = cq.Plane(origin=[0.0, -0.4460584223270416, 0.0], xDir=[0.0, 0.0, 1.0], normal=[0.0, 1.0, 0.0])
result = cq.Workplane(plane).circle(0.49999988079071045).extrude(0.8921168446540833)
