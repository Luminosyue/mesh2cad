import cadquery as cq
plane = cq.Plane(origin=[-0.013281182090097873, -0.0036709739134197956, -0.48400612016289485], xDir=[0.0, -1.0, 0.0], normal=[0.0, 0.0, 1.0])
result = cq.Workplane(plane).circle(0.055109970938903505).extrude(1.0)
