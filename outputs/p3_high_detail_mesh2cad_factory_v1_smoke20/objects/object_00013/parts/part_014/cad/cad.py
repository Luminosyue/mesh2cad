import cadquery as cq
plane = cq.Plane(origin=[-0.5, -0.0015836701404712483, -0.008916399346566153], xDir=[0.0, 0.0, -1.0], normal=[1.0, 0.0, 0.0])
result = cq.Workplane(plane).circle(0.022516603934829026).extrude(1.0)
