import cadquery as cq
plane = cq.Plane(origin=[0.0, 0.0, -0.26799121499061584], xDir=[0.0, -1.0, 0.0], normal=[0.0, 0.0, 1.0])
result = cq.Workplane(plane).circle(0.37798331677913666).extrude(0.5359824299812317)
