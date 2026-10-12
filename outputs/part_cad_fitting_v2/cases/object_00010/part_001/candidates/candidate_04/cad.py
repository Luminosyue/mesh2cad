import cadquery as cq
plane = cq.Plane(origin=[-0.03243371152689603, -0.09449780732393265, 0.058099772705871404], xDir=[0.0, 0.0, 1.0], normal=[0.0, 1.0, 0.0])
result = cq.Workplane(plane).circle(0.407628259385738).extrude(0.1889956146478653)
