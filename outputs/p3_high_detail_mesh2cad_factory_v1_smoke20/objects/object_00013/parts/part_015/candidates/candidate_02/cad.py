import cadquery as cq
plane = cq.Plane(origin=[0.01750241476951256, -0.02735617198050022, 0.20927020751261066], xDir=[0.0, 0.0, 1.0], normal=[0.0, 1.0, 0.0])
result = cq.Workplane(plane).circle(0.4810235155040112).extrude(0.05471234396100044)
