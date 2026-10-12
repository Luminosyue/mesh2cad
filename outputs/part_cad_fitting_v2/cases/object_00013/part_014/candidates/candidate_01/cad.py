import cadquery as cq
plane = cq.Plane(origin=[-0.49709145183629627, -0.00878650813466557, -0.014209677716575182], xDir=[0.0, 0.0, -1.0], normal=[1.0, 0.0, 0.0])
result = cq.Workplane(plane).circle(0.022516603934829026).extrude(1.0)
