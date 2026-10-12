import cadquery as cq
plane = cq.Plane(origin=[-0.19883039593696594, -0.014717585744463274, -19.864041424726626], xDir=[0.0, 0.0, -1.0], normal=[1.0, 0.0, 0.0])
result = cq.Workplane(plane).circle(19.86747811133549).extrude(0.3976607918739319)
