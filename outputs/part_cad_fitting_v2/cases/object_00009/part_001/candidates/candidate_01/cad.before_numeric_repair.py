import cadquery as cq
plane = cq.Plane(origin=[-0.031035466089016764, -0.0008572831708288569, -0.5319137685090538], xDir=[0.0, -1.0, 0.0], normal=[0.0, 0.0, 1.0])
result = cq.Workplane(plane).circle(np.float64(0.20123585859927132)).extrude(np.float64(1.0))
