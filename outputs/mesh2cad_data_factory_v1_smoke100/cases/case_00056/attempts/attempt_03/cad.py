import cadquery as cq
plane = cq.Plane(origin=[-0.011515696533024311, 0.0, 0.0], xDir=[0.0, 0.0, -1.0], normal=[1.0, 0.0, 0.0])
result = cq.Workplane(plane).circle(0.3699176758527756).extrude(0.023031393066048622)
