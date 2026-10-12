import cadquery as cq
plane = cq.Plane(origin=[0.0, -0.5, 0.0], xDir=[0.0, 0.0, 1.0], normal=[0.0, 1.0, 0.0])
p0 = cq.Workplane(plane).polyline([[0.14711792767047882, 0.008097412995994091], [-0.14711792767047882, -0.008097412995994091], [-0.10457666963338852, -0.005755898542702198]]).close().extrude(1.0)
result = p0
