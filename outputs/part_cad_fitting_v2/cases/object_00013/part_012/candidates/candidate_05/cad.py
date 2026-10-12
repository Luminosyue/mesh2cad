import cadquery as cq
plane = cq.Plane(origin=[-0.5, 0.005413464288619036, 0.0014439027832882244], xDir=[0.0, 0.0, -1.0], normal=[1.0, 0.0, 0.0])
result = cq.Workplane(plane).circle(0.021293751925684005).workplane(offset=1.0).circle(0.021145276406132726).loft(ruled=True)
