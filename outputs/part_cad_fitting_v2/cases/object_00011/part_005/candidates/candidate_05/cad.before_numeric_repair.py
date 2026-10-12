import cadquery as cq
plane = cq.Plane(origin=[-0.0009061122434805083, 0.0003080907140280005, -0.5036607238434904], xDir=[0.0, -1.0, 0.0], normal=[0.0, 0.0, 1.0])
result = cq.Workplane(plane).circle(np.float64(0.03925431897122122)).extrude(np.float64(0.9656054162575665))
