import cadquery as cq
plane = cq.Plane(origin=[-0.014914697118565261, -1.7370120671539677, -0.06316780298948288], xDir=[0.0, -1.0, 0.0], normal=[0.0, 0.0, 1.0])
result = cq.Workplane(plane).circle(1.7765794665249013).workplane(offset=0.12633560597896576).circle(1.7990636723535127).loft(ruled=True)
