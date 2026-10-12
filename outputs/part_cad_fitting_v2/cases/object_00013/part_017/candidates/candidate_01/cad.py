import cadquery as cq
plane = cq.Plane(origin=[-0.502573870620633, -0.007779579573459249, 0.014850795613188446], xDir=[0.0, 0.0, -1.0], normal=[1.0, 0.0, 0.0])
result = cq.Workplane(plane).circle(0.022882976751573563).extrude(1.0)
