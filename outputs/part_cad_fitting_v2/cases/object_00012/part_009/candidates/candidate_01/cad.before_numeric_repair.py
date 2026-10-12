import cadquery as cq
plane = cq.Plane(origin=[0.0005223058780543873, -0.5012377918571345, 0.009060566479494879], xDir=[0.0, 0.0, 1.0], normal=[0.0, 1.0, 0.0])
result = cq.Workplane(plane).circle(np.float64(0.021715208234859815)).extrude(np.float64(1.0))
