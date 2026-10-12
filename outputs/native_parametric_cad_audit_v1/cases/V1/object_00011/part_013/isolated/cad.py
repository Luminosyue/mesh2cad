import cadquery as cq
plane = cq.Plane(origin=[-0.0005774854226872461, 0.00039901152335777395, -0.5], xDir=[0.0, -1.0, 0.0], normal=[0.0, 0.0, 1.0])
result = cq.Workplane(plane).circle(0.03715897833195939).extrude(1.0)
