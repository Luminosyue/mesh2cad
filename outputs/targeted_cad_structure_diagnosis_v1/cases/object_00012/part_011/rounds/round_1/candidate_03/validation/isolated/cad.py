import cadquery as cq
plane = cq.Plane(origin=[-0.006125630406986418, -0.48714465195364104, 0.0007208339988222883], xDir=[0.0, 0.0, 1.0], normal=[0.0, 1.0, 0.0])
result = cq.Workplane(plane).circle(0.023982735880503425).extrude(1.0)

feature_1 = cq.Workplane(cq.Plane(origin=[-0.00869125716628567, -0.08750649012865558, 0.029359219535704584], xDir=[0.0, 0.0, 1.0], normal=[0.0, 1.0, 0.0])).rect(0.008168188314284048, 0.02450456494285214).extrude(0.13069101302854472)
result = result.union(feature_1)
