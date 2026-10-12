import cadquery as cq
plane = cq.Plane(origin=[-0.03984349966049194, 0.0, 0.0], xDir=[0.0, 0.0, -1.0], normal=[1.0, 0.0, 0.0])
result = cq.Workplane(plane).circle(0.3442382663488388).extrude(0.07968699932098389)
