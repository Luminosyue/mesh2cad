import cadquery as cq
plane = cq.Plane(origin=[0.0, -0.1656222939491272, 0.0], xDir=[0.0, 0.0, 1.0], normal=[0.0, 1.0, 0.0])
result = cq.Workplane(plane).circle(0.32785698026418686).extrude(0.3312445878982544)
