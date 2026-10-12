import cadquery as cq
plane = cq.Plane(origin=[0.009811274843851428, 0.02485438746069838, -0.33748385310173035], xDir=[0.0, -1.0, 0.0], normal=[0.0, 0.0, 1.0])
result = cq.Workplane(plane).circle(0.4280398923030609).extrude(0.6749677062034607)
