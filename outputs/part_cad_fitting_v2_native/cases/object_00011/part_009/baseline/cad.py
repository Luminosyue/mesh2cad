import cadquery as cq
plane = cq.Plane(origin=[0.004676825991953354, -0.0002249987141549892, -0.5074849957988121], xDir=[0.0, -1.0, 0.0], normal=[0.0, 0.0, 1.0])
result = cq.Workplane(plane).circle(0.03901261668071265).extrude(0.9656054162575665)
