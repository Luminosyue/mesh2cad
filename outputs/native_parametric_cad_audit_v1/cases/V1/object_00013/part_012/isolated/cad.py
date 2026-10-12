import cadquery as cq
plane = cq.Plane(origin=[-0.5, 0.005368240789555004, 0.0016527312577121307], xDir=[0.0, 0.0, -1.0], normal=[1.0, 0.0, 0.0])
result = cq.Workplane(plane).circle(0.020655811442659135).extrude(1.0)
