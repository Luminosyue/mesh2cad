import cadquery as cq
plane = cq.Plane(origin=[0.0, 0.0, -0.002903770888224244], xDir=[0.0, -1.0, 0.0], normal=[0.0, 0.0, 1.0])
result = cq.Workplane(plane).circle(0.4164641350507736).extrude(0.005807541776448488)
