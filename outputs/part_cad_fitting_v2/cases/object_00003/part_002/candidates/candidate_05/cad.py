import cadquery as cq
plane = cq.Plane(origin=[-0.011830887852201625, 0.02034587319054025, -0.36485812067985535], xDir=[0.0, -1.0, 0.0], normal=[0.0, 0.0, 1.0])
result = cq.Workplane(plane).circle(0.5643502972724589).workplane(offset=0.7297162413597107).circle(0.33512536913609253).loft(ruled=True)
