import cadquery as cq
plane = cq.Plane(origin=[0.0005223058780543873, -0.5012377918571345, 0.009060566479494879], xDir=[0.0, 0.0, 1.0], normal=[0.0, 1.0, 0.0])
result = cq.Workplane(plane).circle(0.021715208234859815).extrude(1.0)

feature_1 = cq.Workplane(cq.Plane(origin=[0.009554260320240444, -0.16210887412871083, 0.031334126067738374], xDir=[0.0, 1.0, 0.0], normal=[1.0, 0.0, 0.0])).rect(0.2826074462744497, 0.008074498464984278).extrude(0.008074498464984278)
result = result.cut(feature_1)
