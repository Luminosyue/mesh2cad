import cadquery as cq
plane = cq.Plane(origin=[0.005166394941252775, 0.0002499922392394479, -0.5], xDir=[0.0, -1.0, 0.0], normal=[0.0, 0.0, 1.0])
result = cq.Workplane(plane).circle(0.0377353397030449).extrude(1.0)
