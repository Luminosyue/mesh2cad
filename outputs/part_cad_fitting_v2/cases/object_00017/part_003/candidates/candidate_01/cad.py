import cadquery as cq
plane = cq.Plane(origin=[0.005899094101805294, -0.5025001897569921, 0.06592521232324872], xDir=[0.0, 0.0, 1.0], normal=[0.0, 1.0, 0.0])
result = cq.Workplane(plane).circle(0.28795433265109377).extrude(1.0)
