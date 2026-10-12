import cadquery as cq
plane = cq.Plane(origin=[-0.1020675078034401, -0.00392359054597935, -0.16361375303704512], xDir=[0.0, 0.0, -1.0], normal=[1.0, 0.0, 0.0])
result = cq.Workplane(plane).circle(0.4172750243948142).extrude(0.2041350156068802)
