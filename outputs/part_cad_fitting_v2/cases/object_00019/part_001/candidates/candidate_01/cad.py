import cadquery as cq
plane = cq.Plane(origin=[-0.5048193996391909, -0.17353767533527412, 0.0024872682807690017], xDir=[0.0, 0.0, -1.0], normal=[1.0, 0.0, 0.0])
result = cq.Workplane(plane).circle(0.16801052035525893).extrude(1.0)
