import cadquery as cq
plane = cq.Plane(origin=[0.00838845061050529, -3.282413374783695e-05, -0.5276696057215011], xDir=[0.0, -1.0, 0.0], normal=[0.0, 0.0, 1.0])
result = cq.Workplane(plane).circle(np.float64(0.03656586110061772)).extrude(np.float64(1.0))
