import cadquery as cq
plane = cq.Plane(origin=[-0.00038270443060329606, -0.007349559697479371, -0.5227746904976308], xDir=[0.0, -1.0, 0.0], normal=[0.0, 0.0, 1.0])
result = cq.Workplane(plane).circle(np.float64(0.036197224089559915)).extrude(np.float64(1.0))
