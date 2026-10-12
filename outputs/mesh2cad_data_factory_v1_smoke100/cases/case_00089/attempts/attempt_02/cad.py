import cadquery as cq
plane = cq.Plane(origin=[0.0, -0.04454931244254112, 0.0], xDir=[0.0, 0.0, 1.0], normal=[0.0, 1.0, 0.0])
result = cq.Workplane(plane).circle(0.27927758544683456).extrude(0.08909862488508224)
