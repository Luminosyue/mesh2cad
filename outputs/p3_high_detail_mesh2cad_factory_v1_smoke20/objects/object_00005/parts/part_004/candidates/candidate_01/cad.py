import cadquery as cq
plane = cq.Plane(origin=[-0.44057244062423706, -1.093343399370535, -0.00229418346029592], xDir=[0.0, 0.0, -1.0], normal=[1.0, 0.0, 0.0])
result = cq.Workplane(plane).circle(1.1295132260705538).extrude(0.8811448812484741)
