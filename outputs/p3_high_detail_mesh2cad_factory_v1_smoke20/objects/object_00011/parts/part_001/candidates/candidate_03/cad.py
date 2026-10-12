import cadquery as cq
plane = cq.Plane(origin=[0.008278939552133066, -0.00013156690949809593, -0.5], xDir=[0.0, -1.0, 0.0], normal=[0.0, 0.0, 1.0])
result = cq.Workplane(plane).circle(0.03759962595903681).extrude(1.0)
