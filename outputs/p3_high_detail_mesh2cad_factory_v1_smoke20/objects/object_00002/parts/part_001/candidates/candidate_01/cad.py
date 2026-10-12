import cadquery as cq
plane = cq.Plane(origin=[-0.0012497719122412099, 0.04552268211868528, -0.4940877854824066], xDir=[0.0, -1.0, 0.0], normal=[0.0, 0.0, 1.0])
result = cq.Workplane(plane).circle(0.3907689800101173).extrude(0.9881755709648132)
