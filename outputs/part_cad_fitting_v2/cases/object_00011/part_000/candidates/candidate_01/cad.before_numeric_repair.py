import cadquery as cq
plane = cq.Plane(origin=[-0.0003567404463097003, -0.008775085686590947, -0.5458245414925983], xDir=[0.0, -1.0, 0.0], normal=[0.0, 0.0, 1.0])
result = cq.Workplane(plane).circle(np.float64(0.03454873183687689)).extrude(np.float64(1.0))
