import cadquery as cq
plane = cq.Plane(origin=[0.3840100843051102, -94.7755197479353, -0.06638078391551971], xDir=[0.0, -1.0, 0.0], normal=[0.0, 0.0, 1.0])
result = cq.Workplane(plane).circle(94.74941305181049).extrude(0.13276156783103943)
