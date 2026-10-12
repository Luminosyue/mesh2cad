import cadquery as cq
plane = cq.Plane(origin=[-0.08887347918315142, 0.018812232471212692, -0.30891576409339905], xDir=[0.0, -1.0, 0.0], normal=[0.0, 0.0, 1.0])
result = cq.Workplane(plane).circle(0.3210395260762856).extrude(0.6178315281867981)
