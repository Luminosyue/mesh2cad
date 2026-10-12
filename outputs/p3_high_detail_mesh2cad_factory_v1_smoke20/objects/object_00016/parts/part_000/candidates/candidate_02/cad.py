import cadquery as cq
plane = cq.Plane(origin=[-0.0006718042038882654, -0.10028116523907303, -0.41125398874282837], xDir=[0.0, -1.0, 0.0], normal=[0.0, 0.0, 1.0])
result = cq.Workplane(plane).circle(0.48277323290914054).extrude(0.8225079774856567)
