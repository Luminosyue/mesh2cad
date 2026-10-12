import cadquery as cq
plane = cq.Plane(origin=[0.004529377171499576, -0.5, -0.40206313959289586], xDir=[0.0, 0.0, 1.0], normal=[0.0, 1.0, 0.0])
result = cq.Workplane(plane).circle(0.438876104848622).extrude(1.0)
