import cadquery as cq
plane = cq.Plane(origin=[-0.19188924133777618, 0.008268569899569006, -0.03967277500655568], xDir=[0.0, 0.0, -1.0], normal=[1.0, 0.0, 0.0])
result = cq.Workplane(plane).circle(0.4118883054950518).extrude(0.38377848267555237)
