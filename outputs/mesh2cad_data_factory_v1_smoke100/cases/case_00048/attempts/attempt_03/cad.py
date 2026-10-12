import cadquery as cq
plane = cq.Plane(origin=[0.0, -0.3944137394428253, 0.0], xDir=[0.0, 0.0, 1.0], normal=[0.0, 1.0, 0.0])
result = cq.Workplane(plane).circle(0.3809627890586853).extrude(0.7888274788856506)
