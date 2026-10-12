import cadquery as cq
plane = cq.Plane(origin=[-0.004574888703400265, -1.463607428980353e-05, -0.5327923684109206], xDir=[0.0, -1.0, 0.0], normal=[0.0, 0.0, 1.0])
result = cq.Workplane(plane).circle(0.03711168516388972).extrude(1.0)
