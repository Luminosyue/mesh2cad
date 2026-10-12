import cadquery as cq
plane = cq.Plane(origin=[0.0, -0.4995073974132538, 0.0], xDir=[0.0, 0.0, 1.0], normal=[0.0, 1.0, 0.0])
result = cq.Workplane(plane).circle(0.4939369559288025).extrude(0.9990147948265076)
