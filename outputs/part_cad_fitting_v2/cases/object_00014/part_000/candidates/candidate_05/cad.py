import cadquery as cq
plane = cq.Plane(origin=[-0.010518681940387391, -0.33102089166641235, 1.2413533951805011], xDir=[0.0, 0.0, 1.0], normal=[0.0, 1.0, 0.0])
result = cq.Workplane(plane).circle(1.3945584369930948).workplane(offset=0.6620417833328247).circle(1.314585430363086).loft(ruled=True)
