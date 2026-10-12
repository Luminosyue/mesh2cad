import cadquery as cq
plane = cq.Plane(origin=[-0.5, 0.0009268320137382265, 0.009070939966564818], xDir=[0.0, 0.0, -1.0], normal=[1.0, 0.0, 0.0])
result = cq.Workplane(plane).circle(0.022882976751573563).extrude(1.0)
