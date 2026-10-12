import cadquery as cq
plane = cq.Plane(origin=[-0.03929667165587249, -0.07542889619572721, -0.5], xDir=[0.0, -1.0, 0.0], normal=[0.0, 0.0, 1.0])
result = cq.Workplane(plane).circle(0.22206509231101104).extrude(1.0)
