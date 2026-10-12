import cadquery as cq
plane = cq.Plane(origin=[0.0, 0.0, -0.05036705359816551], xDir=[0.0, -1.0, 0.0], normal=[0.0, 0.0, 1.0])
p0_0 = cq.Workplane(plane).moveTo(-0.14361641384652915,0.0035292860786064885).circle(0.3042635896344354).extrude(0.10073410719633102)
b0 = p0_0
result = b0
