import cadquery as cq
plane = cq.Plane(origin=[-0.010577931272466163, -0.07283138458098745, -0.3188382685184479], xDir=[0.0, -1.0, 0.0], normal=[0.0, 0.0, 1.0])
result = cq.Workplane(plane).circle(0.3843714205732654).extrude(0.6376765370368958)
