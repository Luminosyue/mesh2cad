import cadquery as cq
plane = cq.Plane(origin=[0.008634906960409286, 4.239819299474049e-05, -0.5180275662710141], xDir=[0.0, -1.0, 0.0], normal=[0.0, 0.0, 1.0])
result = cq.Workplane(plane).circle(0.03759962595903681).extrude(1.0)
