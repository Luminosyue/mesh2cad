import cadquery as cq
plane = cq.Plane(origin=[-0.006273132867388807, -0.5, 0.13605104333595158], xDir=[0.0, 0.0, 1.0], normal=[0.0, 1.0, 0.0])
result = cq.Workplane(plane).circle(0.27325677346881694).extrude(1.0)
