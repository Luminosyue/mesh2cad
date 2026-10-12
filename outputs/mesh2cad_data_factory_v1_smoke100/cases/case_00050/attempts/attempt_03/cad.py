import cadquery as cq
plane = cq.Plane(origin=[0.0, 0.0, -0.4721512496471405], xDir=[0.0, -1.0, 0.0], normal=[0.0, 0.0, 1.0])
result = cq.Workplane(plane).circle(0.45394083857536316).extrude(0.944302499294281)
