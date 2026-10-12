import cadquery as cq
plane = cq.Plane(origin=[0.0033367664959643613, 0.8302342309526217, -0.006756911100386778], xDir=[1.0, 0.0, 0.0], normal=[0.0, 0.0, 1.0])
result = cq.Workplane(plane).sphere(0.956954862540806)
