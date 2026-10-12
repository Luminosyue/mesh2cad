import cadquery as cq
plane = cq.Plane(origin=[0.006312730311863384, 3.214797059096494e-05, -0.509367386817305], xDir=[0.0, -1.0, 0.0], normal=[0.0, 0.0, 1.0])
result = cq.Workplane(plane).circle(np.float64(0.03853369613776489)).extrude(np.float64(0.9656054162575665))
