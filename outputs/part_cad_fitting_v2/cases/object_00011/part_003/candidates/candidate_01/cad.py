import cadquery as cq
plane = cq.Plane(origin=[0.011267401802885185, -1.1776283635593315e-05, -0.5306768988910057], xDir=[0.0, -1.0, 0.0], normal=[0.0, 0.0, 1.0])
result = cq.Workplane(plane).circle(0.03700861829212799).extrude(1.0)
