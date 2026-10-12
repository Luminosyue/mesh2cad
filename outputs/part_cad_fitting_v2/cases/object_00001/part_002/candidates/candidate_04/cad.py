import cadquery as cq
plane = cq.Plane(origin=[0.005488421730198322, 0.0007981181129665409, -0.438090980052948], xDir=[0.0, -1.0, 0.0], normal=[0.0, 0.0, 1.0])
result = cq.Workplane(plane).circle(0.4917219752863934).extrude(0.876181960105896)
