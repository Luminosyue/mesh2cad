import cadquery as cq
plane = cq.Plane(origin=[0.0001296142223165219, -0.014620956117382494, -0.5], xDir=[0.0, -1.0, 0.0], normal=[0.0, 0.0, 1.0])
result = cq.Workplane(plane).circle(0.03315151420865424).extrude(1.0)
