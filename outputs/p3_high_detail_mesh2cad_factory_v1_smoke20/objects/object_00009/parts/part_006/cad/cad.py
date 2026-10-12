import cadquery as cq
plane = cq.Plane(origin=[-0.00025879365995340464, -0.021105494437243622, -0.5], xDir=[0.0, -1.0, 0.0], normal=[0.0, 0.0, 1.0])
result = cq.Workplane(plane).circle(0.2693547205493011).extrude(1.0)
