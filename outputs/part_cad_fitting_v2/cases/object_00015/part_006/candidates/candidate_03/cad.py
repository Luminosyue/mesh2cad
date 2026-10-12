import cadquery as cq
plane = cq.Plane(origin=[-0.06938561237469705, -0.04925697296857834, -9.062626383322845], xDir=[0.0, 0.0, 1.0], normal=[0.0, 1.0, 0.0])
result = cq.Workplane(plane).circle(9.049306607095652).extrude(0.09851394593715668)
