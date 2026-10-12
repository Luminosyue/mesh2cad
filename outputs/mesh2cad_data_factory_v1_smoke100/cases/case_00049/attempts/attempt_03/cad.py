import cadquery as cq
plane = cq.Plane(origin=[-0.27756693959236145, 0.0, 0.0], xDir=[0.0, 0.0, -1.0], normal=[1.0, 0.0, 0.0])
result = cq.Workplane(plane).circle(0.4473327249288559).extrude(0.5551338791847229)
