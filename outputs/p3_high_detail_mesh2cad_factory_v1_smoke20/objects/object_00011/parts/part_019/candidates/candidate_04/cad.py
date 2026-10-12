import cadquery as cq
plane = cq.Plane(origin=[-0.014997780629000031, -0.5, -0.007900437787294719], xDir=[0.0, 0.0, 1.0], normal=[0.0, 1.0, 0.0])
result = cq.Workplane(plane).circle(0.041827464942882094).extrude(1.0)
