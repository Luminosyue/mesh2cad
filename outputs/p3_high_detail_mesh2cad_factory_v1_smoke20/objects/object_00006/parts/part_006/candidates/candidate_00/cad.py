import cadquery as cq
plane = cq.Plane(origin=[-0.43863269686698914, -0.504409703991296, -0.011682008616715195], xDir=[0.0, 0.0, -1.0], normal=[1.0, 0.0, 0.0])
result = cq.Workplane(plane).circle(0.5452171123036929).extrude(0.8772653937339783)
