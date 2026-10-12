import cadquery as cq
plane = cq.Plane(origin=[-0.5, 0.028103582095300082, 0.02061945008606763], xDir=[0.0, 0.0, -1.0], normal=[1.0, 0.0, 0.0])
result = cq.Workplane(plane).circle(0.19308155605422286).extrude(1.0)
