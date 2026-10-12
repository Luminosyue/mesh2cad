import cadquery as cq
plane = cq.Plane(origin=[-0.09715194255113602, 0.12187970456610706, -0.7294524009085258], xDir=[0.0, 0.0, -1.0], normal=[1.0, 0.0, 0.0])
result = cq.Workplane(plane).circle(0.8027523375253165).extrude(0.19430388510227203)
