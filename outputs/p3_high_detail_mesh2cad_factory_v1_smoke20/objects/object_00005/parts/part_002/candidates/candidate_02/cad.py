import cadquery as cq
plane = cq.Plane(origin=[-0.012050467682085467, 0.024531979317108703, -0.5], xDir=[0.0, -1.0, 0.0], normal=[0.0, 0.0, 1.0])
result = cq.Workplane(plane).circle(0.11940630011896042).extrude(1.0)
