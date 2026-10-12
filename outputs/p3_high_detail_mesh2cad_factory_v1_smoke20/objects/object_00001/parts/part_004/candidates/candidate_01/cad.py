import cadquery as cq
plane = cq.Plane(origin=[-0.011349066861558427, 0.005830699612008085, -0.2167033702135086], xDir=[0.0, -1.0, 0.0], normal=[0.0, 0.0, 1.0])
result = cq.Workplane(plane).circle(0.3271554806749113).extrude(0.4334067404270172)
