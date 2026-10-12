import cadquery as cq
plane = cq.Plane(origin=[-0.3548071086406708, 2.2894141431507182, 0.001868874108390686], xDir=[0.0, 0.0, -1.0], normal=[1.0, 0.0, 0.0])
result = cq.Workplane(plane).circle(2.386371388213563).extrude(0.7096142172813416)
