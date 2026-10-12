import cadquery as cq
plane = cq.Plane(origin=[1.870550013629179, -0.5, -0.010616569674799271], xDir=[0.0, 0.0, 1.0], normal=[0.0, 1.0, 0.0])
result = cq.Workplane(plane).circle(1.869447345781107).extrude(1.0)
