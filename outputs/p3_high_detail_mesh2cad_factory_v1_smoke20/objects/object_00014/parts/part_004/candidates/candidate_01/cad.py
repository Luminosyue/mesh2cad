import cadquery as cq
plane = cq.Plane(origin=[-0.011960089089250857, -0.37528593214170636, -0.49590590596199036], xDir=[0.0, -1.0, 0.0], normal=[0.0, 0.0, 1.0])
result = cq.Workplane(plane).circle(0.45898997762407584).extrude(0.9918118119239807)
