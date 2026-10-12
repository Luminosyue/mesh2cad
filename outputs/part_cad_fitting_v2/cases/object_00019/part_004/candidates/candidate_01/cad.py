import cadquery as cq
plane = cq.Plane(origin=[-0.5039056269744582, -0.008168119941777038, 0.00431715882100491], xDir=[0.0, 0.0, -1.0], normal=[1.0, 0.0, 0.0])
result = cq.Workplane(plane).circle(0.054071099489506884).extrude(1.0)
