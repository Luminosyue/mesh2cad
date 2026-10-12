import cadquery as cq
plane = cq.Plane(origin=[0.004676825991953354, -0.0002249987141549892, -0.5074849957988121], xDir=[0.0, -1.0, 0.0], normal=[0.0, 0.0, 1.0])
result = cq.Workplane(plane).circle(0.03901261668071265).extrude(0.9656054162575665)

feature_1 = cq.Workplane(cq.Plane(origin=[-0.015752510197701, -0.03770348970447818, -0.48717277545121407], xDir=[-1.0, 0.0, -1.4952704595019295e-33], normal=[-1.4952704595019295e-33, 0.0, 1.0])).circle(0.004062439405149029).extrude(0.9099864267533825)
result = result.cut(feature_1)
