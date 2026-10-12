import cadquery as cq
plane = cq.Plane(origin=[-0.5, 0.011843235151277887, -0.18762375038398357], xDir=[0.0, 0.0, -1.0], normal=[1.0, 0.0, 0.0])
result = cq.Workplane(plane).circle(0.266776809197047).extrude(1.0)
