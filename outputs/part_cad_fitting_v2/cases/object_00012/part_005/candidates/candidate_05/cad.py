import cadquery as cq
plane = cq.Plane(origin=[-0.354434996843338, 2.0632691539496117, 0.0006863860120935493], xDir=[0.0, 0.0, -1.0], normal=[1.0, 0.0, 0.0])
result = cq.Workplane(plane).circle(2.1701110658603997).workplane(offset=0.708869993686676).circle(2.1702224252084394).loft(ruled=True)
