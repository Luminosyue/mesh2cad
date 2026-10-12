import cadquery as cq
plane = cq.Plane(origin=[-0.0009061122187218177, 0.00030809070428497714, -0.5208580157147071], xDir=[0.0, -1.0, 0.0], normal=[0.0, 0.0, 1.0])
result = cq.Workplane(plane).circle(0.03790418301011335).extrude(1.0)

feature_1 = cq.Workplane(cq.Plane(origin=[-0.003247362952078545, -0.0008598969828698042, 0.43825455706927086], xDir=[0.0, -1.0, 0.0], normal=[0.0, 0.0, 1.0])).rect(0.0823272572409722, 0.0823272572409722).extrude(0.041163628620486004)
result = result.cut(feature_1)
