import cadquery as cq
plane = cq.Plane(origin=[0.003101211921878443, 0.023852787041540226, -0.2727906853135797], xDir=[0.0, -1.0, 0.0], normal=[0.0, 0.0, 1.0])
result = cq.Workplane(plane).circle(np.float64(0.4280398923030609)).extrude(np.float64(0.6749677062034607))
