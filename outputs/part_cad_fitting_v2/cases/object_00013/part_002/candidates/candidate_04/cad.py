import cadquery as cq
plane = cq.Plane(origin=[-0.1020675078034401, -0.12276287995901937, -1.1903888582746172], xDir=[0.0, 0.0, -1.0], normal=[1.0, 0.0, 0.0])
result = cq.Workplane(plane).circle(1.3676290629334298).extrude(0.2041350156068802)
