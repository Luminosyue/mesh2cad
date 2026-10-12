import cadquery as cq
plane = cq.Plane(origin=[-0.00024569689937567387, -0.5, 0.013158489543090998], xDir=[0.0, 0.0, 1.0], normal=[0.0, 1.0, 0.0])
result = cq.Workplane(plane).circle(0.025472811012254997).extrude(1.0)
