import cadquery as cq
plane = cq.Plane(origin=[-0.24337243128707453, 0.2950763984628666, -0.5], xDir=[0.0, -1.0, 0.0], normal=[0.0, 0.0, 1.0])
result = cq.Workplane(plane).circle(0.5612099868837291).extrude(1.0)
