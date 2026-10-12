import cadquery as cq
plane = cq.Plane(origin=[0.0, -0.01745106652379036, 0.0], xDir=[0.0, 0.0, 1.0], normal=[0.0, 1.0, 0.0])
result = cq.Workplane(plane).circle(0.2644126396626234).extrude(0.03490213304758072)
