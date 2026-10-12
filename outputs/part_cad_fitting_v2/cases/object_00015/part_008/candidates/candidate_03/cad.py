import cadquery as cq
plane = cq.Plane(origin=[0.024426408402943592, 4.189614864954261, 10.857618335061332], xDir=[1.0, 0.0, 0.0], normal=[0.0, 0.0, 1.0])
result = cq.Workplane(plane).sphere(11.658159732788794)
