import cadquery as cq
plane = cq.Plane(origin=[0.0, 0.0, -0.07680642604827881], xDir=[0.0, -1.0, 0.0], normal=[0.0, 0.0, 1.0])
p0 = cq.Workplane(plane).polyline([[-0.4460294842720032, -0.5], [-0.4460294842720032, 0.5], [0.4460294842720032, 0.5], [0.4460294842720032, -0.5]]).close().extrude(0.15361285209655762)
result = p0
