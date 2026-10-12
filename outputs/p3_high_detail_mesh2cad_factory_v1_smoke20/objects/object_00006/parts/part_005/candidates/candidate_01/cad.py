import cadquery as cq
plane = cq.Plane(origin=[-0.021530428823094333, -1.4300062423184734, -0.3576590120792389], xDir=[0.0, -1.0, 0.0], normal=[0.0, 0.0, 1.0])
result = cq.Workplane(plane).circle(1.4974782669005506).extrude(0.7153180241584778)
