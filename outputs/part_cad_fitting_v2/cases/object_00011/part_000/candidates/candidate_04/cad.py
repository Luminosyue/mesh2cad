import cadquery as cq
plane = cq.Plane(origin=[-0.00020625039764080163, -0.008654108477594432, -0.5], xDir=[0.0, -1.0, 0.0], normal=[0.0, 0.0, 1.0])
result = cq.Workplane(plane).circle(0.031504851170888165).extrude(1.0)
