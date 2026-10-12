import cadquery as cq
plane = cq.Plane(origin=[-0.5, -0.0220534499420416, -0.0016351141319023192], xDir=[0.0, 0.0, -1.0], normal=[1.0, 0.0, 0.0])
result = cq.Workplane(plane).circle(0.09601165685370447).extrude(1.0)
