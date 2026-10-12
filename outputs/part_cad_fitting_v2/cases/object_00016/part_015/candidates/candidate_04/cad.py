import cadquery as cq
plane = cq.Plane(origin=[-0.19883039593696594, -2.1176778109146, -4420.639046608866], xDir=[0.0, 0.0, -1.0], normal=[1.0, 0.0, 0.0])
result = cq.Workplane(plane).circle(4420.641478889159).extrude(0.3976607918739319)
