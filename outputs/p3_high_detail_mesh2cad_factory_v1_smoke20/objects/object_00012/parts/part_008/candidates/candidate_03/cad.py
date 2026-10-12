import cadquery as cq
plane = cq.Plane(origin=[0.2795338513291038, -0.12888087332248688, 0.006069626210939484], xDir=[0.0, 0.0, 1.0], normal=[0.0, 1.0, 0.0])
result = cq.Workplane(plane).circle(0.5139817751505755).extrude(0.25776174664497375)
