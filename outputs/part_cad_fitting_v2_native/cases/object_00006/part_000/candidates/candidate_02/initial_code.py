import cadquery as cq
plane = cq.Plane(origin=[0.0, 0.0, -0.05036705359816551], xDir=[0.0, -1.0, 0.0], normal=[0.0, 0.0, 1.0])
p0 = cq.Workplane(plane).moveTo(-0.143640656712715, 0.0034468525147557717).circle(0.3044759999659656).extrude(0.10073410719633102)
result = p0
