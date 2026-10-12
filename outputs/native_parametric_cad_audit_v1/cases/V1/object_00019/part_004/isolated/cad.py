import cadquery as cq
plane = cq.Plane(origin=[-0.5, -0.009017203078110573, 0.0030044011426942387], xDir=[0.0, 0.0, -1.0], normal=[1.0, 0.0, 0.0])
result = cq.Workplane(plane).circle(0.054071099489506884).extrude(1.0)
