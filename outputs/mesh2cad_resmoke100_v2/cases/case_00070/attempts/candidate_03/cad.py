import cadquery as cq
plane = cq.Plane(origin=[0.0, -0.1083003506064415, 0.0], xDir=[0.0, 0.0, 1.0], normal=[0.0, 1.0, 0.0])
p0 = cq.Workplane(plane).polyline([[-0.5, 0.38584002852439886], [0.5, 0.38584002852439886], [0.5, -0.3858400285243988], [-0.5, -0.3858400285243988]]).close().extrude(0.216600701212883)
result = p0
