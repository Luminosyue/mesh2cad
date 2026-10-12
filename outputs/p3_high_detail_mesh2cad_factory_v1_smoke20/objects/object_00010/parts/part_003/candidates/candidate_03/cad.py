import cadquery as cq
plane = cq.Plane(origin=[-0.10727570950984955, 0.0002644884856848051, 0.12930436247656774], xDir=[0.0, 0.0, -1.0], normal=[1.0, 0.0, 0.0])
result = cq.Workplane(plane).circle(0.28219178305352427).extrude(0.2145514190196991)
