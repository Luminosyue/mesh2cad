import cadquery as cq
plane = cq.Plane(origin=[-0.008624657062414148, 0.00020889437360334335, -0.5], xDir=[0.0, -1.0, 0.0], normal=[0.0, 0.0, 1.0])
result = cq.Workplane(plane).circle(0.036266949144209665).extrude(1.0)
