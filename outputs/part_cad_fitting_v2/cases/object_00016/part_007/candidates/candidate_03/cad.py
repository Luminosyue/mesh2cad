import cadquery as cq
plane = cq.Plane(origin=[3885.7453883777316, 1.2747216923161961, -0.17543859779834747], xDir=[0.0, -1.0, 0.0], normal=[0.0, 0.0, 1.0])
result = cq.Workplane(plane).circle(3885.742924407954).extrude(0.35087719559669495)
