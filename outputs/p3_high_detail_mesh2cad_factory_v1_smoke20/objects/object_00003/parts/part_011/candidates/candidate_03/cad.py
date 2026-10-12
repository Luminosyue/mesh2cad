import cadquery as cq
plane = cq.Plane(origin=[0.05026368120670538, 0.012804293706241008, -0.4845467209815979], xDir=[0.0, -1.0, 0.0], normal=[0.0, 0.0, 1.0])
result = cq.Workplane(plane).circle(0.3903709543029962).extrude(0.9690934419631958)
