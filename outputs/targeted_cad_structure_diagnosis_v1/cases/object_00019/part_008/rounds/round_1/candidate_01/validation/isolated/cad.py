import cadquery as cq
plane = cq.Plane(origin=[0.001552729291263818, -0.5126301164600346, -0.0018061923594058116], xDir=[0.0, 0.0, 1.0], normal=[0.0, 1.0, 0.0])
result = cq.Workplane(plane).circle(0.011983886384736355).extrude(1.0)

feature_1 = cq.Workplane(cq.Plane(origin=[0.007728697608176928, -0.5184403057250786, -0.005305023920253608], xDir=[0.0, 0.0, 1.0], normal=[0.0, 1.0, 0.0])).rect(0.034220659039145854, 0.034220659039145854).extrude(0.045170719630768234)
result = result.cut(feature_1)
