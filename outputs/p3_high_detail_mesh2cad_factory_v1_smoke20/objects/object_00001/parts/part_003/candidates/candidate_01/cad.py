import cadquery as cq
plane = cq.Plane(origin=[-0.2258777587688402, 0.4381861509058984, -0.5], xDir=[0.0, -1.0, 0.0], normal=[0.0, 0.0, 1.0])
result = cq.Workplane(plane).circle(0.711701104853954).extrude(1.0)
