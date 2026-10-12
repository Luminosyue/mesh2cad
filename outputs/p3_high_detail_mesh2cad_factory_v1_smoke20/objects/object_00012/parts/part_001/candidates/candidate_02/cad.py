import cadquery as cq
plane = cq.Plane(origin=[-5.0355512186281426e-05, 0.12511417919206846, -0.5], xDir=[0.0, -1.0, 0.0], normal=[0.0, 0.0, 1.0])
result = cq.Workplane(plane).circle(0.3107015923289754).extrude(1.0)
