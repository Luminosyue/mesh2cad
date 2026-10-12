import cadquery as cq
plane = cq.Plane(origin=[0.007211864922462822, 0.00895823701388826, -0.5], xDir=[0.0, -1.0, 0.0], normal=[0.0, 0.0, 1.0])
result = cq.Workplane(plane).circle(0.041978490392302906).extrude(1.0)
