import cadquery as cq
plane = cq.Plane(origin=[0.0, 0.0, 0.0], xDir=[0.0, 0.0, 1.0], normal=[0.0, 1.0, 0.0])
result = cq.Workplane(plane).box(0.7794117331504822,1.0,0.009959476999938488)
