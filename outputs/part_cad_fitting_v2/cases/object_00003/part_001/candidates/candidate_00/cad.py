import cadquery as cq
plane = cq.Plane(origin=[0.018267752119313974, -0.05519181109166085, -0.2976777255535126], xDir=[0.0, -1.0, 0.0], normal=[0.0, 0.0, 1.0])
result = cq.Workplane(plane).circle(0.3753217655653893).extrude(0.5953554511070251)
