import cadquery as cq
plane = cq.Plane(origin=[-0.025909913925593844, -0.04936742864110224, -0.5], xDir=[0.0, -1.0, 0.0], normal=[0.0, 0.0, 1.0])
result = cq.Workplane(plane).circle(0.19647343539904877).extrude(1.0)
