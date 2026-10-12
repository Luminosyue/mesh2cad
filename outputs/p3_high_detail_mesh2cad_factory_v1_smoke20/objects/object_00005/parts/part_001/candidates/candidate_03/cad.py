import cadquery as cq
plane = cq.Plane(origin=[0.015597499998285743, 0.016334336434074524, -0.5], xDir=[0.0, -1.0, 0.0], normal=[0.0, 0.0, 1.0])
result = cq.Workplane(plane).circle(0.11964513106270964).extrude(1.0)
