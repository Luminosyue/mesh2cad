import cadquery as cq
plane = cq.Plane(origin=[-0.0010309459171116925, -0.5, -0.0009940156581833817], xDir=[0.0, 0.0, 1.0], normal=[0.0, 1.0, 0.0])
result = cq.Workplane(plane).circle(0.03657028384246343).extrude(1.0)
