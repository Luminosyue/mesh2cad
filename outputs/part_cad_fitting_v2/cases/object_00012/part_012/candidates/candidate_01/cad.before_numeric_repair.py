import cadquery as cq
plane = cq.Plane(origin=[-0.0001790416366812928, -0.49093571921552104, 0.014108006190684412], xDir=[0.0, 0.0, 1.0], normal=[0.0, 1.0, 0.0])
result = cq.Workplane(plane).circle(np.float64(0.025472811012254997)).extrude(np.float64(1.0))
