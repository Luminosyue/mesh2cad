import cadquery as cq
plane = cq.Plane(origin=[-0.35350415110588074, 0.04113050381193394, 0.029586003898624827], xDir=[0.0, 0.0, -1.0], normal=[1.0, 0.0, 0.0])
result = cq.Workplane(plane).circle(0.38091426818720897).extrude(0.7070083022117615)
