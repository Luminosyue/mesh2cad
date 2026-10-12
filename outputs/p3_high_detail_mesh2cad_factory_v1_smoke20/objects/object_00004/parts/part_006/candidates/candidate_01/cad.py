import cadquery as cq
plane = cq.Plane(origin=[-0.21434053778648376, 0.001220208641959878, -0.0009340711972480603], xDir=[0.0, 0.0, -1.0], normal=[1.0, 0.0, 0.0])
result = cq.Workplane(plane).circle(0.4670030142398403).extrude(0.42868107557296753)
