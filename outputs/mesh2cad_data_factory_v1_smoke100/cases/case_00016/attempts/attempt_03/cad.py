import cadquery as cq
plane = cq.Plane(origin=[0.0, -0.017854705452919006, 0.0], xDir=[0.0, 0.0, 1.0], normal=[0.0, 1.0, 0.0])
result = cq.Workplane(plane).circle(0.2589273527264595).extrude(0.03570941090583801)
