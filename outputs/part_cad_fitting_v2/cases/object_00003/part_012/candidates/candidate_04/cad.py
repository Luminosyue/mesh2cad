import cadquery as cq
plane = cq.Plane(origin=[-0.0020779465763216733, -1.0474105231252195, -0.1410461962223053], xDir=[0.0, -1.0, 0.0], normal=[0.0, 0.0, 1.0])
result = cq.Workplane(plane).circle(1.1601609981559762).extrude(0.2820923924446106)
