import cadquery as cq
plane = cq.Plane(origin=[-0.3912437856197357, 0.0, 0.0], xDir=[0.0, 0.0, -1.0], normal=[1.0, 0.0, 0.0])
result = cq.Workplane(plane).circle(0.42373092472553253).extrude(0.7824875712394714)
