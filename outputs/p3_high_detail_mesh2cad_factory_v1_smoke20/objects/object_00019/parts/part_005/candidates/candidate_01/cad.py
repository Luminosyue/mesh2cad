import cadquery as cq
plane = cq.Plane(origin=[-0.1259082343510263, 0.13561344680264417, -0.5], xDir=[0.0, -1.0, 0.0], normal=[0.0, 0.0, 1.0])
result = cq.Workplane(plane).circle(0.38640718902982935).extrude(1.0)
