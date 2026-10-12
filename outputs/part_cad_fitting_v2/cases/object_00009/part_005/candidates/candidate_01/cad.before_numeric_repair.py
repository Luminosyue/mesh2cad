import cadquery as cq
plane = cq.Plane(origin=[0.0056045128822073305, -0.029228218310186804, -0.42], xDir=[0.0, -1.0, 0.0], normal=[0.0, 0.0, 1.0])
result = cq.Workplane(plane).circle(np.float64(0.26108573609890107)).extrude(np.float64(1.0))
