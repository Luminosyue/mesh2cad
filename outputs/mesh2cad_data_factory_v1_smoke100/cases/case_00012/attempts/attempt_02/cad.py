import cadquery as cq
plane = cq.Plane(origin=[0.0, 0.0, -0.07680642604827881], xDir=[0.0, -1.0, 0.0], normal=[0.0, 0.0, 1.0])
result = cq.Workplane(plane).circle(0.4730147421360016).extrude(0.15361285209655762)
