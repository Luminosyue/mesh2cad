import cadquery as cq
plane = cq.Plane(origin=[-0.006125630406986418, -0.48714465195364104, 0.0007208339988222883], xDir=[0.0, 0.0, 1.0], normal=[0.0, 1.0, 0.0])
result = cq.Workplane(plane).circle(0.023982735880503425).extrude(1.0)

feature_1 = cq.Workplane(cq.Plane(origin=[-0.0123328374344636, 0.3989432284602094, -0.0200924242389638], xDir=[0.0, 1.0, 0.0], normal=[-0.0, -0.0, -1.0])).rect(0.12048204600014546, 0.024504564942852143).extrude(0.008168188314284048)
result = result.union(feature_1)
