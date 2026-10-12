import cadquery as cq
plane = cq.Plane(origin=[0.004005580870525605, -0.004979738499969244, 0.013463985383013058], xDir=[0.0, 0.0, 1.0], normal=[0.0, 1.0, 0.0])
result = cq.Workplane(plane).circle(0.4612312629584471).extrude(0.009959476999938488)
