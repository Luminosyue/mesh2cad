import cadquery as cq
plane = cq.Plane(origin=[-0.5, -0.0016812717613386386, -0.009001473450413985], xDir=[0.0, 0.0, -1.0], normal=[1.0, 0.0, 0.0])
result = cq.Workplane(plane).circle(0.022336418042250953).extrude(1.0)
