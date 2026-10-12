import cadquery as cq
plane = cq.Plane(origin=[-0.19428600370883942, 0.0, 0.0], xDir=[0.0, 0.0, -1.0], normal=[1.0, 0.0, 0.0])
result = cq.Workplane(plane).circle(0.42142875492572784).extrude(0.38857200741767883)
