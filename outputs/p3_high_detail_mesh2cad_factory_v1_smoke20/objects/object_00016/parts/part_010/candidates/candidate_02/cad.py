import cadquery as cq
plane = cq.Plane(origin=[-4.127591448606999, -0.5, -0.004740162626698346], xDir=[0.0, 0.0, 1.0], normal=[0.0, 1.0, 0.0])
result = cq.Workplane(plane).circle(4.1286560479676115).extrude(1.0)
