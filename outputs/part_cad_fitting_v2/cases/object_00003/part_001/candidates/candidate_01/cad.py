import cadquery as cq
plane = cq.Plane(origin=[0.03435357442202757, -0.03986405042420466, -0.2589260111286278], xDir=[0.0, -1.0, 0.0], normal=[0.0, 0.0, 1.0])
result = cq.Workplane(plane).circle(0.3753217655653893).extrude(0.5953554511070251)
