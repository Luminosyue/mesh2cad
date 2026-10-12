import cadquery as cq
plane = cq.Plane(origin=[0.004676825978746428, -0.0002249987403059198, -0.5246822876700289], xDir=[0.0, -1.0, 0.0], normal=[0.0, 0.0, 1.0])
result = cq.Workplane(plane).circle(np.float64(0.037670793969276424)).extrude(np.float64(1.0))
