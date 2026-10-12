import cadquery as cq
plane = cq.Plane(origin=[-0.0009061122187218177, 0.00030809070428497714, -0.5208580157147071], xDir=[0.0, -1.0, 0.0], normal=[0.0, 0.0, 1.0])
result = cq.Workplane(plane).circle(0.03790418301011335).extrude(1.0)

feature_1 = cq.Workplane(cq.Plane(origin=[-0.0028358153641459853, -0.004530249623707645, -0.5273585016947878], xDir=[0.0, -1.0, 0.0], normal=[0.0, 0.0, 1.0])).circle(0.04871058476961483).extrude(0.03035849570408086)
result = result.cut(feature_1)

feature_2 = cq.Workplane(cq.Plane(origin=[-0.0003084672554846716, -0.0017850497557270976, 0.439516129032258], xDir=[0.0, -1.0, 0.0], normal=[0.0, 0.0, 1.0])).circle(0.04764779768706438).extrude(0.04032258064516137)
result = result.cut(feature_2)
