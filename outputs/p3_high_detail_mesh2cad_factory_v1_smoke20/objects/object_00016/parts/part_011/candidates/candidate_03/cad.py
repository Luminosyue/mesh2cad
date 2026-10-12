import cadquery as cq
plane = cq.Plane(origin=[0.7195044883574943, 0.0027587813460926906, -0.030520154163241386], xDir=[0.0, -1.0, 0.0], normal=[0.0, 0.0, 1.0])
result = cq.Workplane(plane).circle(0.8147666467113717).extrude(0.06104030832648277)
