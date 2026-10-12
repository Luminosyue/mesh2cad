import cadquery as cq
plane = cq.Plane(origin=[-0.0069910398637123335, -0.030061893632653488, -0.0179727537857849], xDir=[0.0, 0.0, 1.0], normal=[0.0, 1.0, 0.0])
result = cq.Workplane(plane).box(np.float64(1.0), np.float64(0.8772653937339783), np.float64(0.1435755342245102))
