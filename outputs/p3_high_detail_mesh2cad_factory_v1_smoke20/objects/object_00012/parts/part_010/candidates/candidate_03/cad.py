import cadquery as cq
plane = cq.Plane(origin=[-0.2387118649474527, -0.1717231422662735, -0.0005536679276373786], xDir=[0.0, 0.0, 1.0], normal=[0.0, 1.0, 0.0])
result = cq.Workplane(plane).circle(0.4968808427313826).extrude(0.343446284532547)
